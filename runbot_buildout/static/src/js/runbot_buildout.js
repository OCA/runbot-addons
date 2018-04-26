//Copyright 2018 Therp BV <https://therp.nl>
//License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
jQuery(document).ready(function() {
    jQuery('a.runbot-rerun-buildout').click(function() {
        return jQuery.ajax(
            _.str.sprintf(
                '/runbot/build/%s/rerun_buildout',
                jQuery(this).data('runbot-build')
            ),
            {method: 'POST'}
        ).then(function() {
            window.location.reload();
        });
    });
});
