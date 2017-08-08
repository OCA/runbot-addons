/* Copyright 2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
 */

odoo.define('runbot_relative.runbot_relative', function(require){
    "use strict";

    var snippet_animation = require('web_editor.snippets.animation');

    snippet_animation.registry.runbot_relative = snippet_animation.Class.extend({

        selector: 'a',

        start: function() {
            var domains = [
                $('#runbot-host').val(),
                $('#runbot-domain').val()
            ];
            var elHref = this.$el.attr('href')
            var elHost = this.getHostname(elHref);
            if ( ! domains.includes(elHost) ) {
                return;
            }
            this.$el.attr('href', elHref.replace(/https?:/, ''));
        },

        getHostname: function(uri) {
            // Remove protocol
            var split = uri.split('/')
            var host = (uri.indexOf('://') > -1) ? split[2] : split[0];
            // Remove port
            host = host.split(':')[0];
            // Remove query args
            host = host.split('?')[0];
            return host;
        }

    });

});
