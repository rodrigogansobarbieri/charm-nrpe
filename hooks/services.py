from charmhelpers.core import hookenv
from charmhelpers.core.services.base import ServiceManager
from charmhelpers.core.services import helpers

import nrpe_utils
import nrpe_helpers


def manage():
    config = hookenv.config()
    manager = ServiceManager([
        {
            'service': 'nrpe-install',
            'data_ready': [
                nrpe_utils.install_packages,
                nrpe_utils.install_charm_files,
            ],
        },
        {
            'service': 'nrpe-config',
            'required_data': [
                config,
                nrpe_helpers.MonitorsRelation(),
                nrpe_helpers.PrincipleRelation(),
                nrpe_helpers.NagiosInfo(),
            ],
            'data_ready': [
                nrpe_utils.update_nrpe_external_master_relation,
                nrpe_utils.update_monitor_relation,
                nrpe_utils.create_host_export_fragment,
                nrpe_utils.render_nrped_files,
                helpers.render_template(
                    source='nrpe.tmpl',
                    target='/etc/nagios/nrpe.cfg'
                ),
            ],
            'provided_data': [nrpe_helpers.PrincipleRelation()],
            'start': [nrpe_utils.restart_nrpe],
        },
        {
            'service': 'nrpe-rsync',
            'required_data': [
                config,
                nrpe_helpers.PrincipleRelation(),
                nrpe_helpers.RsyncEnabled(),
                nrpe_helpers.NagiosInfo(),
            ],
            'data_ready': [
                nrpe_utils.remove_host_export_fragments,
                helpers.render_template(
                    source='rsync-juju.d.tmpl',
                    target='/etc/rsync-juju.d/010-nrpe-external-master.conf'
                ),
                nrpe_utils.create_host_export_fragment,
            ],
            'start': [nrpe_utils.restart_rsync],
        },
    ])
    manager.manage()
