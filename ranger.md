### how-ranger-audit-works
```
Ranger plugins send their audit event (whether access was granted or not and based on which policy) directly to the configured sink for audits, which can be HDFS, Solr or both.
Ranger Audit is a highly customizable event queue system which can be tailored to suit the needs of production environments.
When the plugin is enabled AND no specific policy is in place for access to some object, the plugin will fall back to enforcing the standard component level Access Control Lists (ACL’s). For HDFS that would be the user : rwx / group : rwx / other : rwx ACL’s on folders and files.
Once this defaulting to component ACL’s happens the audit events show a ‘ - ‘ in the ‘Policy ID’ column instead of a policy number. If a Ranger policy was in control of allowing/denying the policy number is shown.

Key Things to Remember
1. Access decisions taken by Ranger (to allow / deny user) are based on combination of three things:

a. resource - that is being accessed
b. user/group - who is trying to access
c. operation - that is being performed

2. The Audit decision taken by Ranger (whether to audit or not) are based on matching resource. That is, if there is a policy which allows audit for a certain resource, then audit will be performed irrespective of whether that policy is governing access policy or not.

3. Now based on #1 and #2 above,Depending on policy configuration, it is very much possible that access decision is taken by policy X but audit decision is taken by policy Y.

Note : Sometime this may seems confusing that audit events show a ‘ X‘ in the ‘Policy ID’ column even though audit audit is disabled for X , but remember Policy ID column decided on access decision but audit decision is coming from another policy,

In below Example audit event is captured, and the policy ID is ‘1’ but Audit logging is disabled for policy ‘1’

How to Troubleshoot Ranger Audit issue ?

Enable the ranger plugin debug and restart the host service again to get the root cause of the error.
To get further granular level behaviour understanding enable policyengine & policyevaluator debug as below
For example, (below log4j lines will change based on the host service & log4j module used in that service)

log4j.logger.org.apache.ranger.authorization.hbase=DEBUG

log4j.logger.org.apache.ranger.plugin.policyengine=DEBUG

log4j.logger.org.apache.ranger.plugin.policyevaluator=DEBUG
```
### ranger hdfs plugin not working
```
Do you have keberized environment ? -> You need to enable addon settings if you are using kerberos

Are you using Namenode HA ? -> You need to enable addon settings if you are using Namenode HA

Check below things if "Test Connection" is failing -

1. Check HDFS plugin is enable in "Services->HDFS->Configs->Advanced ranger-hdfs-plugin-properties" and you must restart the service after enabling the plugin.

2. After you enable HDFS plugin, Login to Ranger UI->Audit->Plugins-> You should see "Http Response Code 200" for HDFS service. This means your plugin is in sync properly.

3. Login to the any one of HDFS node [ex. namenode] and check below folder and make sure policy json exist and has updated contents -

ls /etc/ranger/<cluster_name>_hadoop/policycache/ <-- you will see json file in this location. Make sure you have same policy updated here. This makes sure policy is in sync.

4. Sometimes policy not able to connect to plugin. Try restarting the HDFS service and re-check.

Debug -

1. Enable debug in below file -

vi /usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/log4j.xml

Replace - <priority value="info" to <priority value="debug" and restart ranger service.

You should see debug logs in "/var/log/ranger/admin/xa_portal.log"

Also check "/var/log/hadoop/hdfs/hadoop-hdfs-namenode-<hostname>.log" for errors.

ranger hadoop plugin 日志位置/var/log/hadoop/hdfs/namenode.log
//ranger连接信息
provider.AuditProviderFactory (AuditProviderFactory.java:init(150)) - AUDIT PROPERTY: ranger.plugin.hdfs.policy.rest.url
//ranger policy刷新日志，可以看出远程连接ranger server失败，导致无法更新策略
ERROR util.PolicyRefresher (PolicyRefresher.java:loadPolicyfromPolicyAdmin(288)) - PolicyRefresher(serviceName=BaiRong_hadoop): failed to refresh policies. Will continue to use last known version of policies (14)
com.sun.jersey.api.client.ClientHandlerException: java.net.UnknownHostException:
```