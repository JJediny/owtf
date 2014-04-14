from framework.lib.general import cprint
from framework.lib import general
from framework.interface import custom_handlers
import tornado.web

class PluginDataHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET'] #, 'POST', 'PUT', 'PATCH', 'DELETE']
    #TODO: Creation of user plugins

    @tornado.web.asynchronous
    def get(self, plugin_group = None, plugin_type = None, plugin_code = None):
        try:
            filter_data = dict(self.request.arguments)
            if not plugin_group: # First check if plugin_group is present in url
                self.write(self.application.Core.DB.Plugin.GetAll(filter_data))
            if plugin_group and (not plugin_type) and (not plugin_code):
                filter_data.update({"group":plugin_group})
                self.write(self.application.Core.DB.Plugin.GetAll(filter_data))
            if plugin_group and plugin_type and (not plugin_code):
                if plugin_type not in self.application.Core.DB.Plugin.GetTypesForGroup(plugin_group):
                    raise tornado.web.HTTPError(400)
                filter_data.update({"type":plugin_type, "group":plugin_group})
                self.write(self.application.Core.DB.Plugin.GetAll(filter_data))
            if plugin_group and plugin_type and plugin_code:
                if plugin_type not in self.application.Core.DB.Plugin.GetTypesForGroup(plugin_group):
                    raise tornado.web.HTTPError(400)
                filter_data.update({"type":plugin_type, "group":plugin_group, "code":plugin_code})
                self.write(self.application.Core.DB.Plugin.GetAll(filter_data))
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

class TargetConfigHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    @tornado.web.asynchronous
    def get(self, target_id=None):
        try:
            # If no target_id, means /target is accessed with or without filters
            if not target_id:
                # Get all filter data here, so that it can be passed
                filter_data = dict(self.request.arguments)
                self.write(self.application.Core.DB.Target.GetTargetConfigs(filter_data))
            else:
                self.write(self.application.Core.DB.Target.GetTargetConfigForID(target_id))
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def post(self, target_id = None):
        if (target_id) or (not self.get_argument("TARGET_URL", default=None)): # How can one post using an id xD
            raise tornado.web.HTTPError(400)
        try:
            self.application.Core.DB.Target.AddTarget(str(self.get_argument("TARGET_URL")))
            self.set_status(201) # Stands for "201 Created"
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(409)

    @tornado.web.asynchronous
    def put(self, target_id=None):
        return self.patch(target_id)

    @tornado.web.asynchronous
    def patch(self, target_id = None):
        if not target_id or not self.request.arguments:
            raise tornado.web.HTTPError(400)
        try:
            patch_data = dict(self.request.arguments)
            self.application.Core.DB.Target.UpdateTarget(patch_data, ID=target_id)
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def delete(self, target_id = None):
        if not target_id:
            raise tornado.web.HTTPError(400)
        try:
            self.application.Core.DB.Target.DeleteTarget(ID = target_id)
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

class TransactionDataHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET', 'DELETE']

    @tornado.web.asynchronous
    def get(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                self.write(self.application.Core.DB.Transaction.GetByIDAsDict(int(transaction_id), target_id=int(target_id)))
            else:
                # Empty criteria ensure all transactions
                filter_data = dict(self.request.arguments)
                self.write(self.application.Core.DB.Transaction.GetAllAsDicts(filter_data, target_id=int(target_id)))
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except general.InvalidTransactionReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except general.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def post(self, target_url):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def put(self):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def patch(self):
        #TODO: Allow modification of transactions from the UI, may be adjusting scope etc.. But I don't understand it's use yet ;)
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def delete(self, target_id=None, transaction_id=None):
        try:
            if transaction_id:
                self.application.Core.DB.Transaction.DeleteTransaction(int(transaction_id), int(target_id))
            else:
                raise tornado.web.HTTPError(400)
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

class URLDataHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET']

    @tornado.web.asynchronous
    def get(self, target_id=None):
        try:
            # Empty criteria ensure all transactions
            filter_data = dict(self.request.arguments)
            self.write(self.application.Core.DB.URL.GetAll(filter_data, target_id=target_id))
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def post(self, target_url):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def put(self):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def patch(self):
        #TODO: allow modification of urls from the ui, may be adjusting scope etc.. but i don't understand it's use yet ;)
        raise tornado.web.httperror(405)

    @tornado.web.asynchronous
    def delete(self, target_id=None):
        #TODO: allow deleting of urls from the ui
        raise tornado.web.httperror(405)

class PluginOutputHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    @tornado.web.asynchronous
    def get(self, target_id = None, plugin_group = None, plugin_type = None, plugin_code = None):
        try:
            filter_data = dict(self.request.arguments)
            if not plugin_group: # First check if plugin_group is present in url
                self.write(self.application.Core.DB.POutput.GetAll(filter_data, target_id))
            if plugin_group and (not plugin_type):
                filter_data.update({"plugin_group":plugin_group})
                self.write(self.application.Core.DB.POutput.GetAll(filter_data, target_id))
            if plugin_type and plugin_group and (not plugin_code):
                if plugin_type not in self.application.Core.DB.Plugin.GetTypesForGroup(plugin_group):
                    raise tornado.web.HTTPError(400)
                filter_data.update({"plugin_type":plugin_type, "plugin_group":plugin_group})
                self.write(self.application.Core.DB.POutput.GetAll(filter_data, target_id))
            if plugin_type and plugin_group and plugin_code:
                if plugin_type not in self.application.Core.DB.Plugin.GetTypesForGroup(plugin_group):
                    raise tornado.web.HTTPError(400)
                filter_data.update({"plugin_type":plugin_type, "plugin_group":plugin_group, "plugin_code":plugin_code})
                self.write(self.application.Core.DB.POutput.GetAll(filter_data, target_id))
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except general.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def post(self, target_url):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def put(self):
        raise tornado.web.HTTPError(405)

    @tornado.web.asynchronous
    def patch(self, target_id = None, plugin_group = None, plugin_type = None, plugin_code = None):
        try:
            if (not target_id) or (not plugin_group) or (not plugin_type) or (not plugin_code):
                raise tornado.web.httperror(400)
            else:
                patch_data = dict(self.request.arguments)
                self.application.Core.DB.POutput.Update(plugin_group, plugin_type, plugin_code, patch_data, targte_id)
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPErro(400)
        except general.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def delete(self, target_id=None, plugin_group = None, plugin_type = None, plugin_code = None):
        try:
            filter_data = dict(self.request.arguments)
            if not plugin_group: # First check if plugin_group is present in url
                self.application.Core.DB.POutput.DeleteAll(filter_data, target_id)
            if plugin_group and (not plugin_type):
                filter_data.update({"plugin_group":plugin_group})
                self.application.Core.DB.POutput.DeleteAll(filter_data, target_id)
            if plugin_type and plugin_group and (not plugin_code):
                if plugin_type not in self.application.Core.DB.Plugin.GetTypesForGroup(plugin_group):
                    raise tornado.web.HTTPError(400)
                filter_data.update({"plugin_type":plugin_type, "plugin_group":plugin_group})
                self.application.Core.DB.POutput.DeleteAll(filter_data, target_id)
            if plugin_type and plugin_group and plugin_code:
                if plugin_type not in self.application.Core.DB.Plugin.GetTypesForGroup(plugin_group):
                    raise tornado.web.HTTPError(400)
                filter_data.update({"plugin_type":plugin_type, "plugin_group":plugin_group, "plugin_code":plugin_code})
                self.application.Core.DB.POutput.DeleteAll(filter_data, target_id)
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except general.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

class WorkerHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET']

    @tornado.web.asynchronous
    def get(self, worker_id = None, action = None):
        if not worker_id:
            self.write(self.application.Core.WorkerManager.get_worker_details())
        try:
            if worker_id and (not action):
                self.write(self.application.Core.WorkerManager.get_worker_details(int(worker_id)))
            if worker_id and action:
                getattr(self.application.Core.WorkerManager, action + '_worker')(int(worker_id))
        except general.InvalidWorkerReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        self.finish()

class WorkListHandler(custom_handlers.APIRequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST']
    @tornado.web.asynchronous
    def get(self):
        self.write(self.application.Core.WorkerManager.get_work_list())
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        try:
            filter_data = dict(self.request.arguments)
            plugin_list = self.application.Core.DB.Plugin.GetAll(filter_data)
            target_list = self.application.Core.DB.Target.GetTargetConfigs(filter_data)
            if (not plugin_list) or (not target_list):
                raise tornado.web.HTTPError(400)
            self.application.Core.WorkerManager.fill_work_list(target_list, plugin_list)
            self.set_status(201) # TODO: Set proper response code
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except general.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    @tornado.web.asynchronous
    def delete(self):
        try:
            filter_data = dict(self.request.arguments)
            plugin_list = self.application.Core.DB.Plugin.GetAll(filter_data)
            target_list = self.application.Core.DB.Target.GetTargetConfigs(filter_data)
            self.application.Core.WorkerManager.filter_work_list(target_list, plugin_list)
            self.finish()
        except general.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except general.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
