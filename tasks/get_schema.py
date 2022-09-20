# Credit:  Jason Lantz, https://gist.github.com/jlantz/1d1b9703ec9076c704e69e3a37b3246c
# Author:  Katie Kodes, https://katiekodes.com

'''
#############################################################################
Data type notes:

cumulusci.salesforce_api.org_schema.Schema data type notes:
    A "Schema"-typed Python object is easiest to work with by just putting code that handles it under a "with" statement.
    It gets mad if you try to simply assign the return value to a variable on one line
    and then parse the variable with things like its "org_schema[Object_Name_Here__c]" syntax:
    "Error: '_GeneratorContextManager' object is not subscriptable".
    A "Schema"-typed Python object has properties of:
    'add_counts', 'block_writing', 'close', 'engine', 'filters', 'from_cache', 'get', 
    'included_objects', 'includes_counts', 'items', 'keys', 'last_modified_date', 
    'path', 'populate_cache', 'session', 'sobjects', 'values'
    (".values()" is a list of cumulusci.salesforce_api.org_schema_models.SObject)
    (".keys()" is a list of str)
    (".items()" is a dict of str, cumulusci.salesforce_api.org_schema_models.SObject)

cumulusci.salesforce_api.org_schema_models.SObject data type notes:
    An "SObject"-typed Python object has properties of:
    'actionOverrides', 'activateable', 'childRelationships', 'compactLayoutable', 'count', 'createable',
    'custom', 'customSetting', 'deepCloneable', 'defaultImplementation', 'deletable', 'deprecatedAndHidden',
    'extendedBy', 'extendsInterfaces', 'extractable', 'feedEnabled', 'fields', 'hasSubtypes',
    'implementedBy', 'implementsInterfaces', 'isInterface', 'isSubtype', 'keyPrefix',
    'label', 'labelPlural', 'layoutable', 'listviewable', 'lookupLayoutable', 'mergeable', 'metadata', 'mruEnabled',
    'name', 'namedLayoutInfos', 'networkScopeFieldName', 'queryable', 'recordTypeInfos', 'registry', 'replicateable', 'retrieveable',
    'searchLayoutable', 'searchable', 'sobjectDescribeOption', 'supportedScopes', 'triggerable', 'undeletable', 'updateable', 'urls'
    The "sqlalchemy.orm.collections.MappedCollection" dictionary-like object returned by appending ".fields" is often useful
    (it behaves like a native Python dict of "str", "cumulusci.salesforce_api.org_schema_models.Field" with
    ".keys()" that returns a "dict_keys", ".values()" that returns a "dict_values", ".items()" that returns a "dict_items", etc.),
    as are the strings returned by ".name" (Salesforce object's API name) and ".label" (Salesforce object's human-friendly name).

cumulusci.salesforce_api.org_schema_models.Field data type notes:
    A "Field"-typed Python object has properties of:
    'aggregatable', 'aiPredictionField', 'autoNumber', 'byteLength', 
    'calculated', 'calculatedFormula', 'cascadeDelete', 'caseSensitive', 'compoundFieldName', 'controllerName', 'createable', 'custom', 
    'defaultValue', 'defaultValueFormula', 'defaultedOnCreate', 'dependentPicklist', 'deprecatedAndHidden', 'digits', 'displayLocationInDecimal', 
    'encrypted', 'externalId', 'extraTypeInfo', 'filterable', 'filteredLookupInfo', 'formulaTreatNullNumberAsZero', 
    'groupable', 'highScaleNumber', 'htmlFormatted', 'idLookup', 'inlineHelpText', 
    'label', 'length', 'mask', 'maskType', 'metadata', 'name', 'nameField', 'namePointing', 'nillable', 
    'parent', 'permissionable', 'picklistValues', 'polymorphicForeignKey', 'precision', 'queryByDistance', 
    'referenceTargetField', 'referenceTo', 'registry', 'relationshipName', 'relationshipOrder', 
    'requiredOnCreate', 'restrictedDelete', 'restrictedPicklist', 
    'scale', 'searchPrefilterable', 'soapType', 'sobject', 'sortable', 'type', 'unique', 'updateable', 'writeRequiresMasterRead'
    The ".picklistValues" property returns a list of dicts, each of which have:
        'active' (Boolean), 'defaultValue' (Boolean), 'label' (String), validFor (not sure of data type), & 'value' (String).
#############################################################################
'''

from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from cumulusci.salesforce_api.org_schema import get_org_schema
import json
import os

this_python_codebase_path = os.path.realpath(os.path.dirname(__file__))
up_one_folder = os.path.abspath(os.path.join(this_python_codebase_path, '..'))
output_folder = os.path.abspath(os.path.join(up_one_folder, 'output'))

# Class declaration makes this code runnable with a "cci task run" command


class SchemaDetailDumper(BaseSalesforceApiTask):
    # task_options lets "cci task run" commands know what parameters to insist upon
    task_options = {
        "filename": {"required": True, "description": "The filename under an \"output\" folder in this project that you'd like to dump schema data into"},
        "objects": {"required": False, "description": "The list objects to dump schema details of"},
    }

    def __dictify_field_object(self, the_field_name, the_field_object):
        if not isinstance(the_field_name, str):
            print(the_field_name, type(the_field_name))
        native_dict_field = dict()
        for field_property in [x for x in dir(the_field_object) if not x.startswith('_') and not x.startswith('__') and x not in ['fields', 'parent', 'registry', 'metadata']]:
            native_dict_field[field_property] = the_field_object[field_property]
        return native_dict_field

    def __dictify_table_object(self, the_table_name, the_table_object):
        if not isinstance(the_table_name, str):
            print(the_table_name, type(the_table_name))
        native_dict_table = dict()
        for table_property in [x for x in dir(the_table_object) if not x.startswith('_') and not x.startswith('__') and x not in ['fields', 'registry', 'metadata']]:
            native_dict_table[table_property] = the_table_object[table_property]
        native_dict_table['fields'] = {field_name: self.__dictify_field_object(
            field_name, field_object) for field_name, field_object in the_table_object['fields'].items()}
        return native_dict_table

    def __get_full_schema_dict(self, relevant_org_schema):
        allowed_table_names = [] if ( 'objects' not in self.options or self.options['objects'] is None ) else self.options['objects']
        allow_all_tables = (len(allowed_table_names) == 0)
        native_dict_schema = {}
        for table_name, table_object in relevant_org_schema.items():
            if allow_all_tables or table_name in allowed_table_names:
                native_dict_schema[table_name] = self.__dictify_table_object(
                    table_name, table_object)
        return native_dict_schema

    # _run_task function declaration makes this code runnable with a "cci task run" command
    def _run_task(self):
        # "self.sf" & "self.org_config" represent org-login state that the "cci task run" context knows.
        # "self.options" is a dict-like data structure of details you put into your "cumulusci.yml" file.
        # get_org_schema() returns a Python object called "cumulusci.salesforce_api.org_schema.Schema".
        output_filename = self.options['filename']
        if len(output_filename) == 0:
            self.logger.info('Please pass in a proper filename.')
            return  # Short-circuit
        with get_org_schema(self.sf, self.org_config) as org_schema:
            self.logger.info('Downloaded Salesforce org config.  Beginning parsing of results.')
            processed_schema = self.__get_full_schema_dict(org_schema)
            if not processed_schema or len(processed_schema) == 0:
                self.logger.info('There is no data to write to disk.')
                return  # Short-circuit
            os.makedirs(output_folder, exist_ok=True)
            output_filepath = os.path.abspath(
                os.path.join(output_folder, output_filename))
            with open(output_filepath, 'w') as f:
                json.dump(processed_schema, f, indent=2)
            self.logger.info('Data written to disk at:')
            self.logger.info(output_filepath)