# -*- encoding: utf-8 -*-
#TODO: license from vauxoo
from openerp.osv import fields, osv
import oerplib
from openerp import tools

class runbot_prebuild(osv.osv):
    _inherit = "runbot.prebuild"

    _columns = {
        'lang': fields.selection(tools.scan_languages(),'Language', help='Language that will be '\
        'assigned to users in the instance generated'),
    }
    
class runbot_build(osv.osv):
    _inherit = "runbot.build"

    _columns = {
        'lang': fields.selection(tools.scan_languages(),'Language', help='Language that will be '\
        'assigned to users in the instance generated'),
    }
    
    def job_90_load_lang(self, cr, uid, build, lock_path, log_path):
        db_name = build.dest + '-all'
        port = build.port + 1
        user = 'admin'
        passwd = 'admin'
        server = 'localhost'
        code_lang = build.lang
        conect = oerplib.OERP(
            server = server,
            database = db_name,
            port = port,
            )  

        conect.login(user, passwd)
        conect.config['timeout'] = 1000000
        print 'code_lang', code_lang
        if code_lang:
            lang_id = conect.search('res.lang', [('code', '=', code_lang)])
            if not lang_id:
                base_lang_obj = conect.get('base.language.install')
                try:
                    lang_create_id = conect.create('base.language.install', {'lang': code_lang,})
                    base_lang_obj.lang_install([lang_create_id])
                except Exception as e:
                    print e.oerp_traceback
                lang_id = conect.search('res.lang', [('code', '=', code_lang)])
            if lang_id:
                conect.write('res.users', conect.search('res.users', []), {'lang': code_lang})

        
