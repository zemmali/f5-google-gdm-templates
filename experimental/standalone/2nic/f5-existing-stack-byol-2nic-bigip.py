# Copyright 2017 F5 Networks All rights reserved.
#
# Version v1.0.0 

"""Creates BIG-IP"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'
def GenerateConfig(context):
  resources = [{
      'name': 'bigip1-' + context.env['deployment'],
      'type': 'compute.beta.instance',
      'properties': {
          'zone': context.properties['availabilityZone1'],
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/zones/',
                                  context.properties['availabilityZone1'], '/machineTypes/',
                                  context.properties['instanceType']]),
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/f5-5616-pmteam-beta',
                                          '/global/images/',
                                          context.properties['imageName'],
                                         ])
              }
          }],
          'networkInterfaces': [
            {
              'network': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/global/networks/',
                                  context.properties['mgmtNetwork']]),
              'subnetwork': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/regions/',
                                  context.properties['region'], '/subnetworks/',
                                  context.properties['mgmtSubnet']]),
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }],
            },
            {
              'network': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/global/networks/',
                                  context.properties['network1']]),
              'subnetwork': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/regions/',
                                  context.properties['region'], '/subnetworks/',
                                  context.properties['subnet1']]),
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }],
          }],
          'metadata': {
              'items': [{
                  'key': 'output',
                  'value': 'Testing',  
                  'key': 'startup-script',
                  'value': (''.join(['#!/bin/bash\n',
                                    'if [ -f /config/startupFinished ]; then\n',
                                    '    exit\n',
                                    'fi\n',
                                    'mkdir -p /config/cloud/gce\n',
                                    'cat <<\'EOF\' > /config/installCloudLibs.sh\n',
                                    '#!/bin/bash\n',
                                    'echo about to execute\n',
                                    'checks=0\n',
                                    'while [ $checks -lt 120 ]; do echo checking mcpd\n',
                                    '    tmsh -a show sys mcp-state field-fmt | grep -q running\n',
                                    '    if [ $? == 0 ]; then\n',
                                    '        echo mcpd ready\n',
                                    '        break\n',
                                    '    fi\n',
                                    '    echo mcpd not ready yet\n',
                                    '    let checks=checks+1\n',
                                    '    sleep 10\n',
                                    'done\n',
                                    'echo loading verifyHash script\n',
                                    'if ! tmsh load sys config merge file /config/verifyHash; then\n',
                                    '    echo cannot validate signature of /config/verifyHash\n',
                                    '    exit\n',
                                    'fi\n',
                                    'echo loaded verifyHash\n',
                                    'declare -a filesToVerify=(\"/config/cloud/f5-cloud-libs.tar.gz\")\n',
                                    'for fileToVerify in \"${filesToVerify[@]}\"\n',
                                    'do\n',
                                    '    echo verifying \"$fileToVerify\"\n',
                                    '    if ! tmsh run cli script verifyHash \"$fileToVerify\"; then\n',
                                    '        echo \"$fileToVerify\" is not valid\n',
                                    '        exit 1\n',
                                    '    fi\n',
                                    '    echo verified \"$fileToVerify\"\n',
                                    'done\n',
                                    'mkdir -p /config/cloud/gce/node_modules\n',
                                    'echo expanding f5-cloud-libs.tar.gz\n',
                                    'tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/gce/node_modules\n',
                                    'touch /config/cloud/cloudLibsReady\n',
                                    'EOF\n',                                   
                                    'cat <<\'EOF\' > /config/verifyHash\n',
                                    'cli script /Common/verifyHash {\n',
                                    '    proc script::run {} {\n',
                                    '        if {[catch {\n',
                                    '            set hashes(f5-cloud-libs.tar.gz) 1e7b5cb66e140bb4c5650b225612905e17bd167556b0b4366efce2d9138f8be86eec51c09eb96c3ffc2d25ba8965bae840e9d43b7c42dab08cdfad4d3d152509\n',
                                    '            set hashes(f5-cloud-libs-aws.tar.gz) 549aa436be806c80640f8dce570128fdf84613bf0688392e018639412c63818d25f26635b0aaf23e8cdf60b0d331de9218ed51a9cdfbf33db6e683727169a727\n',
                                    '            set hashes(f5-cloud-libs-azure.tar.gz) a4ff4a9af058ce6058159531fd7bca07eb8808cdd1b1e13de0e1324ec7e4692211991ecaa58dc36021c6c88c7783837d480584393753c3dfc2fddf623781e3a9\n',
                                    '            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n',
                                    '            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n',
                                    '            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n',
                                    '            set hashes(f5.http.v1.2.0rc7.tmpl) 21f413342e9a7a281a0f0e1301e745aa86af21a697d2e6fdc21dd279734936631e92f34bf1c2d2504c201f56ccd75c5c13baa2fe7653213689ec3c9e27dff77d\n',
                                    '            set hashes(f5.aws_advanced_ha.v1.3.0rc1.tmpl) 9e55149c010c1d395abdae3c3d2cb83ec13d31ed39424695e88680cf3ed5a013d626b326711d3d40ef2df46b72d414b4cb8e4f445ea0738dcbd25c4c843ac39d\n',
                                    '            set hashes(f5.aws_advanced_ha.v1.4.0rc1.tmpl) de068455257412a949f1eadccaee8506347e04fd69bfb645001b76f200127668e4a06be2bbb94e10fefc215cfc3665b07945e6d733cbe1a4fa1b88e881590396\n',
                                    '            set hashes(asm-policy.tar.gz) 2d39ec60d006d05d8a1567a1d8aae722419e8b062ad77d6d9a31652971e5e67bc4043d81671ba2a8b12dd229ea46d205144f75374ed4cae58cefa8f9ab6533e6\n',
                                    '            set hashes(deploy_waf.sh) 4c125f7cbc4d701cf50f03de479ebe99a08c2b2c3fa6aae3e229eb3f0bba98bb513d630368229c98e7c5c907e6a3168ece2f8f576267514bad4f6730ea14d454\n',
                                    '            set hashes(f5.policy_creator.tmpl) 54d265e0a573d3ae99864adf4e054b293644e48a54de1e19e8a6826aa32ab03bd04c7255fd9c980c3673e9cd326b0ced513665a91367add1866875e5ef3c4e3a\n',
                                    '            set hashes(f5.service_discovery.tmpl) 8d7491accdb1818f09353cd5b03d317ccd87e6801ac25b47aa49984a0f4ca313e8f3ecc1c9c904ce01c89dfeeacd3487655c8d45cc43f83c2ccd54d71f4f7d5f\n',
                                    'EOF\n',
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' >> /config/verifyHash\n',
                                    '            set file_path [lindex $tmsh::argv 1]\n',
                                    '            set file_name [file tail $file_path]\n',
                                    'EOF\n',
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' >> /config/verifyHash\n',
                                    '            if {![info exists hashes($file_name)]} {\n',
                                    '                tmsh::log err \"No hash found for $file_name\"\n',
                                    '                exit 1\n',
                                    '            }\n',
                                    'EOF\n',
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' >> /config/verifyHash\n',
                                    '            set expected_hash $hashes($file_name)\n',
                                    '            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n',
                                    '            if { $expected_hash eq $computed_hash } {\n',
                                    '                exit 0\n',
                                    '            }\n',
                                    '            tmsh::log err \"Hash does not match for $file_path\"\n',
                                    '            exit 1\n',
                                    '        }]} {\n',
                                    '            tmsh::log err {Unexpected error in verifyHash}\n',
                                    '            exit 1\n',
                                    '        }\n',
                                    '    }\n',
                                    '    script-signature AFE2XgLHOiehaIUPzg72a5DrSmRciYP6BwVBIjNvwFiOdQqP+R4SBDzvrWbOiD+k97y8LthVlNbgQ4t2Elo8zMHHLdj62CmxB8KQSzZ1WVxHWiHIyakLri/RcoPVOeo4Tu/VZ78ICmw6SaH7tApcZUjsrTNLv7D8FLDysf9WRM+6eaDQ4FrxhDralIN989Xf2s0MUdH8RF7+FK8RIK7P7SFJDLIqsrHTl75EfNPOMTny/0dv6BO9G5Q6E0ik8quccbtPtAHrXA/dotqAvvvtYisNF3D4mMfTaRBhJYnN/W05syJDX+D95UtpK4F5DY2BmVBdQ9lvucnvMHrhEjbq9g==\n',
                                    '    signing-key /Common/f5-irule\n',
                                    '}\n',
                                    'EOF\n',                                    
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' > /config/waitThenRun.sh\n',
                                    '#!/bin/bash\n',
                                    'while true; do echo \"waiting for cloud libs install to complete\"\n',
                                    '    if [ -f /config/cloud/cloudLibsReady ]; then\n',
                                    '        break\n',
                                    '    else\n',
                                    '        sleep 10\n',
                                    '    fi\n',
                                    'done\n',
                                    '\"$@\"\n',
                                    'EOF\n',
                                    'cat <<\'EOF\' > /config/cloud/gce/custom-config.sh\n',
                                    '#!/bin/bash\n',
                                    '# Grab ip address assined to 1.1\n',
                                    'INT1ADDRESS=`curl \"http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/1/ip\" -H \"Metadata-Flavor: Google\"`\n',
                                    '# Determine network from self ip and netmask given\n',
                                    'prefix2mask() {\n',
                                    '   local i mask=""\n',
                                    '   local octets=$(($1/8))\n',
                                    '   local part_octet=$(($1%8))\n',
                                    '   for ((i=0;i<4;i+=1)); do\n',
                                    '       if [ $i -lt $octets ]; then\n',
                                    '           mask+=255\n',
                                    '       elif [ $i -eq $octets ]; then\n',
                                    '           mask+=$((256 - 2**(8-$part_octet)))\n',
                                    '       else\n',
                                    '           mask+=0\n',
                                    '       fi\n',  
                                    '       test $i -lt 3 && mask+=.\n',
                                    '   done\n',
                                    '   echo $mask\n',
                                    '}\n',
                                    'dotmask=`prefix2mask ',
                                    context.properties['mask1'],
                                    '`\n',
                                    'IFS=. read -r i1 i2 i3 i4 <<< ${INT1ADDRESS}\n',
                                    'IFS=. read -r m1 m2 m3 m4 <<< ${dotmask}\n',
                                    'network=`printf "%d.%d.%d.%d\n" "$((i1 & m1))" "$((i2 & m2))" "$((i3 & m3))" "$((i4 & m4))"`\n',
                                    'GATEWAY=$(echo "`echo $network |cut -d"." -f1-3`.$((`echo $network |cut -d"." -f4` + 1))")\n',
                                    'PROGNAME=$(basename $0)\n',
                                    'function error_exit {\n',
                                    'echo \"${PROGNAME}: ${1:-\\\"Unknown Error\\\"}\" 1>&2\n',
                                    'exit 1\n',
                                    '}\n',                                   
                                    'date\n',
                                    'declare -a tmsh=()\n',
                                    'echo \'starting tmsh config\'\n',
                                    'tmsh+=(\n',
                                    '\"tmsh create net vlan external interfaces add { 1.1 }\"\n',
                                    '\"tmsh create net self ${INT1ADDRESS}/32 vlan external\"\n',
                                    '\"tmsh create net route ext_gw_int network ${GATEWAY}/32 interface external\"\n',
                                    '\"tmsh create net route ext_rt network ${network}/',
                                    context.properties['mask1'],
                                    ' gw ${GATEWAY}.1\"\n',
                                    '\"tmsh save /sys config\")\n',
                                    'for CMD in \"${tmsh[@]}\"\n',
                                    'do\n',
                                    '    if $CMD;then\n',
                                    '        echo \"command $CMD successfully executed.\"\n',
                                    '    else\n',
                                    '        error_exit \"$LINENO: An error has occurred while executing $CMD. Aborting!\"\n',
                                    '    fi\n',
                                    'done\n',
                                    'date\n',
                                    '### START CUSTOM CONFIGURATION\n',
                                    '### END CUSTOM CONFIGURATION\n',
                                    'EOF\n',
                                    'cat <<\'EOF\' > /config/cloud/gce/rm-password.sh\n',
                                    '#!/bin/bash\n',
                                    'date\n',
                                    'echo \'starting rm-password.sh\'\n',
                                    'rm /config/cloud/gce/.adminPassword\n',
                                    'date\n',
                                    'EOF\n',
                                    'curl -s -f --retry 20 -o /config/cloud/f5-cloud-libs.tar.gz https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/v3.3.1/dist/f5-cloud-libs.tar.gz\n',
                                    'chmod 755 /config/verifyHash\n',
                                    'chmod 755 /config/installCloudLibs.sh\n',
                                    'chmod 755 /config/waitThenRun.sh\n',
                                    'chmod 755 /config/cloud/gce/custom-config.sh\n',
                                    'chmod 755 /config/cloud/gce/rm-password.sh\n',
                                    'nohup /usr/bin/setdb provision.1nicautoconfig disable &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/installCloudLibs.sh &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --signal PASSWORD_CREATED --file f5-rest-node --cl-args \'/config/cloud/gce/node_modules/f5-cloud-libs/scripts/generatePassword --file /config/cloud/gce/.adminPassword\' --log-level verbose -o /var/log/generatePassword.log &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --wait-for PASSWORD_CREATED --signal ADMIN_CREATED --file /config/cloud/gce/node_modules/f5-cloud-libs/scripts/createUser.sh --cl-args \'--user admin --password-file /config/cloud/gce/.adminPassword\' --log-level debug -o /var/log/createUser.log &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/onboard.js --port 443 --ssl-port ',
                                    context.properties['manGuiPort'],
                                    ' --wait-for ADMIN_CREATED -o /var/log/onboard.log --log-level debug --no-reboot --host localhost --user admin --password-url file:///config/cloud/gce/.adminPassword --ntp 0.us.pool.ntp.org --ntp 1.us.pool.ntp.org --tz UTC ',
                                    ' --module ltm:nominal --license ',
                                    context.properties['licenseKey1'],
                                    ' --ping &>> /var/log/cloudlibs-install.log < /dev/null &\n',                                   
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --file /config/cloud/gce/custom-config.sh --cwd /config/cloud/gce -o /var/log/custom-config.log --log-level debug --wait-for ONBOARD_DONE --signal CUSTOM_CONFIG_DONE &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --file /config/cloud/gce/rm-password.sh --cwd /config/cloud/gce -o /var/log/rm-password.log --log-level debug --wait-for CUSTOM_CONFIG_DONE --signal PASSWORD_REMOVED &>> /var/log/cloudlibs-install.log < /dev/null &\n',        
                                    'touch /config/startupFinished\n',
                                    ])
                            )
              }]
          }
      }
  }]
  outputs = [{
      'name': 'bigipIP',
      'value': ''.join(['$(ref.' + context.env['name'] + '-' + context.env['deployment'] + '.bigipIP)'])
  }] 
  return {'resources': resources}