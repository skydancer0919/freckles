# -*- coding: utf-8 -*-
import copy
import logging
import pprint
from collections import OrderedDict

from ruamel.yaml.comments import CommentedMap, CommentedSeq
from six import string_types

from frutils import string_is_templated, replace_strings_in_obj, get_template_keys
from frutils.defaults import OMIT_VALUE
from frutils.exceptions import ParametersException
from frutils.parameters import FrutilsNormalizer
from .defaults import DEFAULT_FRECKLES_JINJA_ENV, FRECKLET_NAME
from .exceptions import FrecklesConfigException

log = logging.getLogger("freckles")

DEFAULT_INHERIT_ARGS_LEVEL = 0

#
# def remove_omit_values(item):
#     """Removes all key/value pairs that contain the the omit marker."""
#     if not hasattr(item, "items"):
#         return item
#     else:
#         # TODO: check for lists
#         return {
#             key: remove_omit_values(value)
#             for key, value in item.items()
#             if not isinstance(value, string_types)
#             or (isinstance(value, string_types) and OMIT_VALUE not in value)
#         }


def get_var_item_from_arg_tree(arg_tree_list, var_key):

    for item in arg_tree_list:

        key = item.get("var", None)
        if key == var_key:
            return item

    return None


def remove_duplicate_args(args_list):
    result = CommentedMap()
    meta_dict = {}

    for arg_name, schema, meta, frecklets in args_list:
        if arg_name == "omit":
            continue

        if arg_name not in result.keys():
            result[arg_name] = schema
            meta_dict[arg_name] = meta
            continue

        level = meta["__frecklet_level__"]
        current_level = meta_dict[arg_name]["__frecklet_level__"]

        if level <= current_level:
            result[arg_name] = schema
            meta_dict[arg_name] = meta
            continue

        # existing_schema = result[arg_name]
        #
        # print(existing_schema)
        # print(schema)
        # continue
        #
        # if existing_schema.get("type", "string") != schema.get(
        #     "type", "string"
        # ) or existing_schema.get("schema", {}) != schema.get("schema", {}):
        #     log.debug(
        #         "Multiple arguments with name '{}', but different details: {} -> {}".format(
        #             arg_name, existing_schema, schema
        #         )
        #     )
        #     raise Exception(
        #         "Multiple arguments with name '{}', but different details.".format(
        #             arg_name
        #         )
        #     )

        # result[arg_name] = schema
        # meta_dict[arg_name] = meta

    return result, meta_dict


def add_user_input(tasklist, arg_values):
    """Creates a high-level vars dict out of user input.
    """
    for task in tasklist:
        vars = create_vars_for_task_item(task, arg_values)
        task["input"] = vars


def create_vars_for_task_item(task_item, arg_values):
    """Creates the high level vars for this task.
    """
    # TODO: currently, this does not extract args that are only used in the 'task' key, but not 'vars'
    arg_tree = task_item["arg_tree"]
    vars = {}

    for details in arg_tree:

        try:
            key, value = create_var_value(details, arg_values)
            if key is None:
                continue
            vars[key] = value
        except (Exception) as e:
            # TODO: double check this is ok
            if "__skip__" in task_item[FRECKLET_NAME].keys():
                log.debug("Invalid var, assuming this task will be skipped later on.")
            else:
                raise e

    return vars


def validate_var(key_name, value, schema, password_coerced=True):

    schema = copy.deepcopy(schema)
    schema.pop("doc", None)
    schema.pop("cli", None)
    schema.pop("__meta__", None)
    schema.pop("dependencies", None)  # we only validate a single argument here
    if password_coerced:
        schema.pop("coerce", None)

    if schema.get("type", "string") == "password":
        schema["type"] = "string"

    s = {key_name: schema}
    if value is not None:
        d = {key_name: value}
    else:
        d = {}

    val = FrutilsNormalizer(s)
    valid = val.validated(d)

    if valid is None:
        raise ParametersException(d, val.errors)

    if value is not None:
        return valid[key_name]
    else:
        return None


def create_var_value(arg_branch, arg_values):

    var_key = arg_branch["var"]
    schema = arg_branch["schema"]
    value = arg_branch.get("value", None)

    if "values" in arg_branch.keys():

        values = arg_branch["values"]

        # this is a root var
        # if value is None and len(values) == 1:
        #     v =

        r = {"omit": OMIT_VALUE}
        for child_details in values:
            k, v = create_var_value(child_details, arg_values)
            if k is None:
                continue
            r[k] = v

        if value is None and var_key in r.keys():

            v = r[var_key]

        else:

            if value is None:
                # should be an ignored tasks
                return (None, None)

            else:

                # need to figure out whether we need to do the templating or not
                do_templating = False
                if isinstance(value, string_types):
                    do_templating = string_is_templated(
                        value, jinja_env=DEFAULT_FRECKLES_JINJA_ENV
                    )
                elif isinstance(
                    value,
                    (dict, CommentedMap, OrderedDict, list, set, CommentedSeq, tuple),
                ):
                    do_templating = True

                if do_templating:
                    child_template_keys = get_template_keys(
                        value, jinja_env=DEFAULT_FRECKLES_JINJA_ENV
                    )

                    if not child_template_keys:

                        v = value
                        # raise Exception("Probably a bug, invalid key: {}".format(value))
                    else:
                        try:
                            v = replace_strings_in_obj(
                                value,
                                replacement_dict=r,
                                jinja_env=DEFAULT_FRECKLES_JINJA_ENV,
                            )
                        except (Exception) as e:
                            raise FrecklesConfigException(
                                "Could not process template (error: {}):\n\n{}".format(
                                    e, value
                                )
                            )
                else:
                    v = value

        if not isinstance(v, bool) and not v:
            v = None

        # TODO: test for other var types than string
        if isinstance(v, string_types) and OMIT_VALUE in v:
            return (None, None)
        try:
            # import pp
            # print("------")
            # pp(var_key)
            # pp(v)
            # pp(schema)
            if v is not None and schema.get("type", None) == "string":
                v = str(v)

            validated = validate_var(var_key, v, schema)
            return (var_key, validated)
        except (ParametersException) as e:

            raise FrecklesConfigException(
                "Invalid or missing argument '{}':\n\nvalue:\n{}\n\nschema:\n{}\n\n  => {}".format(
                    var_key, pprint.pformat(value), pprint.pformat(schema), e.errors
                )
            )

    else:

        return extract_var_value(var_key, schema, arg_branch, arg_values)


def extract_var_value(var_key, schema, arg_branch, arg_values):

    if not string_is_templated(var_key, DEFAULT_FRECKLES_JINJA_ENV):
        if "value" in arg_branch.keys():
            value = arg_branch["value"]
        else:
            if var_key in arg_values.keys():
                value = arg_values[var_key]
            elif "default" in schema.keys():
                value = schema["default"]
            else:
                return (None, None)

    if "__meta__" in schema:
        temp_schema = copy.deepcopy(schema)
        temp_schema.pop("__meta__")
    else:
        temp_schema = schema
    try:
        validated = validate_var(var_key, value, temp_schema)

        return (var_key, validated)
    except (ParametersException) as e:
        raise FrecklesConfigException(
            "Invalid (or missing) var '{}':\n\nvalue:\n{}\n\nschema:\n{}\n\n  => {}".format(
                var_key, pprint.pformat(value), pprint.pformat(temp_schema), e.errors
            )
        )
        # return (var_key, value)

    else:
        raise Exception("This is a bug, please report.")


def extract_base_args(tasklist, inherit_args_mode=DEFAULT_INHERIT_ARGS_LEVEL):
    """Extract the base args that are needed as input for this tasklist.

    Args:
        tasklist (list): the tasklist

    Returns:
        dict: the args dict
    """
    result = []
    for task in tasklist:
        args = extract_base_args_from_task_item(task)
        result.extend(args)

    args, meta_dict = remove_duplicate_args(result)

    # convert all children arguments into options
    for n, d in args.items():
        level = meta_dict[n]["__frecklet_level__"]
        if level == 0:
            continue
        if d.get("cli", {}).get("param_type", "option") == "argument":
            d["cli"]["param_type"] = "option"

    if inherit_args_mode == 0:

        temp = CommentedMap()
        for arg, details in args.items():
            level = meta_dict[arg]["__frecklet_level__"]
            # required = details.get("required", False)
            # required = False
            # if level == 0 or required:
            if level == 0:
                # print("YES")
                # print(arg)
                # import pp
                # pp(details)
                # pp(meta_dict[arg])
                # print("--------------")
                temp[arg] = details
            else:
                pass
                # print("NOT")
                # print(arg)
                # import pp
                # pp(details)
                # pp(meta_dict[arg])
                # print("--------------")
        args = temp
    elif inherit_args_mode < 0:
        pass
    else:
        temp = CommentedMap()
        for arg, details in args.items():
            level = meta_dict[arg]["__frecklet_level__"]
            # required = details.get("required", False)
            # required = False
            # if level < inherit_args_mode + 1 or required:
            if level < inherit_args_mode + 1:
                temp[arg] = details
        args = temp

    # import pp
    # print(readable_yaml(args))

    # sort order
    sorted_args = OrderedDict()
    for n in sorted(args.keys()):
        sorted_args[n] = args[n]

    return sorted_args


def extract_base_args_from_task_item(task_item):
    """Extract args needed for a task item.

    Args:
        task_item (dict): the task item

    Returns:
        dict: the args
    """

    args_tree = task_item["arg_tree"]

    args = []

    for item in args_tree:

        args_list = parse_arg_tree_branch(item, base_arg_list=[])

        args.extend(args_list)

    return args


def parse_arg_tree_branch(branch, base_arg_list=[]):
    """Parses a single arg tree branch.

    Args:
        branch (dict): the arg_tree branch

    Returns:
        the parent leaf or value
    """

    branch_key = branch["var"]

    if "values" in branch.keys():

        # key = branch["key"]
        values = branch["values"]
        for child_value in values:

            parse_arg_tree_branch(child_value, base_arg_list=base_arg_list)

    else:
        if "value" in branch.keys():
            # this means we have a value already
            return base_arg_list

        schema = branch["schema"]
        meta = branch["__meta__"]
        frecklets = branch[FRECKLET_NAME]
        base_arg_list.append((branch_key, schema, meta, frecklets))

    return base_arg_list
