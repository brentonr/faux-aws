import re
import lxml.etree as etree

ec2ActionTagLookup = {
    'DescribeInstances': 'reservationSet',
    'DescribeTags': 'tagSet'
}

ec2FilterTranslation = {
    #'affinity': "affinity='%s'",
    #'architecture': "architecture='%s'",
    #'availability-zone': "availability-zone='%s'",
    #'block-device-mapping.attach-time': "block-device-mapping.attach-time='%s'",
    #'block-device-mapping.delete-on-termination': "block-device-mapping.delete-on-termination='%s'",
    #'block-device-mapping.device-name': "block-device-mapping.device-name='%s'",
    #'block-device-mapping.status': "block-device-mapping.status='%s'",
    #'block-device-mapping.volume-id': "block-device-mapping.volume-id='%s'",
    #'client-token': "client-token='%s'",
    #'dns-name': "dns-name='%s'",
    #'group-id': "group-id='%s'",
    #'group-name': "group-name='%s'",
    #'host-Id': "host-Id='%s'",
    #'hypervisor': "hypervisor='%s'",
    #'iam-instance-profile.arn': "iam-instance-profile.arn='%s'",
    #'image-id': "image-id='%s'",
    #'instance-id': "instance-id='%s'",
    #'instance-lifecycle': "instance-lifecycle='%s'",
    #'instance-state-code': "instance-state-code='%s'",
    'instance-state-name': "descendant::ec2:instanceState/ec2:name='%s'",
    #'instance-type': "instance-type='%s'",
    #'instance.group-id': "instance.group-id='%s'",
    #'instance.group-name': "instance.group-name='%s'",
    #'ip-address': "ip-address='%s'",
    #'kernel-id': "kernel-id='%s'",
    #'key-name': "key-name='%s'",
    #'launch-index': "launch-index='%s'",
    #'launch-time': "launch-time='%s'",
    #'monitoring-state': "monitoring-state='%s'",
    #'owner-id': "owner-id='%s'",
    #'placement-group-name': "placement-group-name='%s'",
    #'platform': "platform='%s'",
    #'private-dns-name': "private-dns-name='%s'",
    #'private-ip-address': "private-ip-address='%s'",
    #'product-code': "product-code='%s'",
    #'product-code.type': "product-code.type='%s'",
    #'ramdisk-id': "ramdisk-id='%s'",
    #'reason': "reason='%s'",
    #'requester-id': "requester-id='%s'",
    #'reservation-id': "reservation-id='%s'",
    #'root-device-name': "root-device-name='%s'",
    #'root-device-type': "root-device-type='%s'",
    #'source-dest-check': "source-dest-check='%s'",
    #'spot-instance-request-id': "spot-instance-request-id='%s'",
    #'state-reason-code': "state-reason-code='%s'",
    #'state-reason-message': "state-reason-message='%s'",
    #'subnet-id': "subnet-id='%s'",
    r'tag:(.+)': r"(descendant::ec2:tagSet/ec2:item/ec2:key='\1' and descendant::ec2:tagSet/ec2:item/ec2:value='%s')",
    #'tag-key': "tag-key='%s'",
    #'tag-value': "tag-value='%s'",
    #'tenancy': "tenancy='%s'",
    #'virtualization-type': "virtualization-type='%s'",
    #'vpc-id': "vpc-id='%s'",
    #'network-interface.description': "network-interface.description='%s'",
    #'network-interface.subnet-id': "network-interface.subnet-id='%s'",
    #'network-interface.vpc-id': "network-interface.vpc-id='%s'",
    #'network-interface.network-interface-id': "network-interface.network-interface-id='%s'",
    #'network-interface.owner-id': "network-interface.owner-id='%s'",
    #'network-interface.availability-zone': "network-interface.availability-zone='%s'",
    #'network-interface.requester-id': "network-interface.requester-id='%s'",
    #'network-interface.requester-managed': "network-interface.requester-managed='%s'",
    #'network-interface.status': "network-interface.status='%s'",
    #'network-interface.mac-address': "network-interface.mac-address='%s'",
    #'network-interface-private-dns-name': "network-interface-private-dns-name='%s'",
    #'network-interface.source-dest-check': "network-interface.source-dest-check='%s'",
    #'network-interface.group-id': "network-interface.group-id='%s'",
    #'network-interface.group-name': "network-interface.group-name='%s'",
    #'network-interface.attachment.attachment-id': "network-interface.attachment.attachment-id='%s'",
    #'network-interface.attachment.instance-id': "network-interface.attachment.instance-id='%s'",
    #'network-interface.attachment.instance-owner-id': "network-interface.attachment.instance-owner-id='%s'",
    #'network-interface.addresses.private-ip-address': "network-interface.addresses.private-ip-address='%s'",
    #'network-interface.attachment.device-index': "network-interface.attachment.device-index='%s'",
    #'network-interface.attachment.status': "network-interface.attachment.status='%s'",
    #'network-interface.attachment.attach-time': "network-interface.attachment.attach-time='%s'",
    #'network-interface.attachment.delete-on-termination': "network-interface.attachment.delete-on-termination='%s'",
    #'network-interface.addresses.primary': "network-interface.addresses.primary='%s'",
    #'network-interface.addresses.association.public-ip': "network-interface.addresses.association.public-ip='%s'",
    #'network-interface.addresses.association.ip-owner-id': "network-interface.addresses.association.ip-owner-id='%s'",
    #'association.public-ip': "association.public-ip='%s'",
    #'association.ip-owner-id': "association.ip-owner-id='%s'",
    #'association.allocation-id': "association.allocation-id='%s'",
    #'association.association-id': "association.association-id='%s'",
}

def filter(action, root, filters):
    def upperCaser(matchGroup):
        return matchGroup.group(1).upper()

    ns = { 'ec2': 'http://ec2.amazonaws.com/doc/2015-10-01/' }
    baseTag = ec2ActionTagLookup[action]
    for f in filters:
        filterName = "descendant::ec2:" + re.sub('-([a-z])', upperCaser, f.name).replace('.', 'ec2:') + "='%s'"
        for translationKey, translationValue in ec2FilterTranslation.iteritems():
            matchGroup = re.match(translationKey, f.name)
            if matchGroup:
                filterName = re.sub(translationKey, translationValue, f.name)
                break

        queryValues = []
        for v in f.values:
            queryValue = filterName % v
            queryValues.append(queryValue)
        query = "./ec2:item[" + ' or '.join(queryValues) + "]"
        baseSet = root.xpath("./ec2:" + baseTag, namespaces=ns)
        for base in baseSet:
            matches = base.xpath(query, namespaces=ns)
            for e in base.xpath("./ec2:item", namespaces=ns):
                if not e in matches:
                    base.remove(e)
