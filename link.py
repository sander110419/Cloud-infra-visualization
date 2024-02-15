from lxml.etree import SubElement, Element

def link_nics_to_vms(compute_client, network_client, resource_groups, root_element, resource_node_ids):
    for rg in resource_groups:
        vms = compute_client.virtual_machines.list(rg.name)
        for vm in vms:
            nic_ref = vm.network_profile.network_interfaces[0].id
            nic_name = nic_ref.split('/')[-1]
            nic = network_client.network_interfaces.get(rg.name, nic_name)

            # Get the IDs of the VM and NIC nodes
            vm_id = resource_node_ids[vm.name]
            nic_id = resource_node_ids[nic.name]

            # Create an edge between the VM and NIC nodes
            print(f"Linked NIC {nic_id} to {vm_id}")
            edge = SubElement(root_element, 'mxCell', {'id': f'{vm_id}-{nic_id}', 'value': '', 'edge': '1', 'source': nic_id, 'target': vm_id, 'parent': '1'})
            edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

    return root_element

def link_dbs_to_servers(sql_client, resource_groups, root_element, resource_node_ids):
    for rg in resource_groups:
        servers = sql_client.servers.list_by_resource_group(rg.name)
        for server in servers:
            dbs = sql_client.databases.list_by_server(rg.name, server.name)
            for db in dbs:
                # Get the IDs of the Server and DB nodes
                server_id = resource_node_ids[server.name]
                db_id = resource_node_ids[f"{server.name}/{db.name}"]  # Use the combined server and database name as the key

                # Create an edge between the Server and DB nodes
                print(f"Linked DB {db_id} to {server_id}")
                edge = SubElement(root_element, 'mxCell', {'id': f'{server_id}-{db_id}', 'value': '', 'edge': '1', 'source': server_id, 'target': db_id, 'parent': '1'})
                edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

    return root_element

def link_disks_to_vms(compute_client, resource_groups, root_element, resource_node_ids):
    for rg in resource_groups:
        vms = compute_client.virtual_machines.list(rg.name)
        for vm in vms:
            # Get the IDs of the VM node
            vm_id = resource_node_ids[vm.name]

            # Get the associated disks of the VM
            data_disks = vm.storage_profile.data_disks
            os_disk = vm.storage_profile.os_disk

            for disk in data_disks:
                # Extract disk name from disk id
                disk_name = disk.managed_disk.id.split('/')[-1]
                if disk_name in resource_node_ids:
                    # Get the IDs of the Disk nodes
                    disk_id = resource_node_ids[disk_name]

                    # Create an edge between the VM and Disk nodes
                    print(f"Linked Data Disk {disk_id} to {vm_id}")
                    edge = SubElement(root_element, 'mxCell', {'id': f'{vm_id}-{disk_id}', 'value': '', 'edge': '1', 'source': disk_id, 'target': vm_id, 'parent': '1'})
                    edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

            # Do the same for the OS disk
            if os_disk is not None:
                os_disk_name = os_disk.managed_disk.id.split('/')[-1]
                if os_disk_name in resource_node_ids:
                    os_disk_id = resource_node_ids[os_disk_name]
                    print(f"Linked OS Disk {os_disk_id} to {vm_id}")
                    edge = SubElement(root_element, 'mxCell', {'id': f'{vm_id}-{os_disk_id}', 'value': '', 'edge': '1', 'source': os_disk_id, 'target': vm_id, 'parent': '1'})
                    edge.append(Element('mxGeometry', {'relative': '1', 'as': 'geometry'}))

    return root_element