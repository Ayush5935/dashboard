dashboard "eni_detail" {
  title = "AWS Network Analyzer Detail"

  input "source_account_input" {
    title = "Select Source Account:"
    type  = "select"
    query = query.account_table
    width = 2
  }

  input "sregion_input" {
    title = "Select Source Region:"
    type  = "select"
    width = 2
    option "us-east-1" {}
    option "us-east-2" {}
    option "us-west-1" {}
    option "us-west-2" {}
  }

  input "ipv4_input" {
    title = "Select a Source Private IPv4 :"
    query = query.ipv4_input
    width = 3
    args  = {
      "account_id" = source_account_input.value
      "region"     = sregion_input.value
    }
  }

  input "eni_source_input" {
    title = "Select a Source ENI:"
    type  = "select"
    query = query.eni_input
    width = 4
    args  = {
      "account_id" = source_account_input.value
      "region"     = sregion_input.value
      "ipv4"       = ipv4_input.value
    }
  }

  input "subnet_source_input" {
    title = "Select a Source Subnet ID:"
    type  = "select"
    width = 4
    query = query.subnet_input
    args  = [eni_source_input.value]
  }

  input "route_table_source_input" {
    title = "Select a Source Route Table ID:"
    type  = "select"
    width = 4
    query = query.route_table_input
    args  = [subnet_source_input.value]
  }

  input "source_routes_input" {
    title = "Select Source Routes:"
    type  = "select"
    width = 4
    query = query.source_routes
    args  = [subnet_source_input.value]
  }

  input "source_transit_gateway_input" {
    title = "Select Source Transit Gateway:"
    type  = "select"
    width = 4
    query = query.source_transit_gateway
    args  = [subnet_source_input.value]
  }

  input "transit_gateway_attachment_input" {
    title = "Select Transit Gateway Attachment:"
    type  = "select"
    width = 4
    query = query.transit_gateway_attachment
    args  = [source_transit_gateway_input.value]
  }

  container {
    card {
      width = 3
      query = query.eni_status
      args  = [eni_source_input.value]
    }
    card {
      width = 3
      query = query.termination_status
      args  = [eni_source_input.value]
    }
  }

  container {
    container {
      width = 6
      table {
        title = "Source ENI Overview"
        type  = "line"
        width = 4
        query = query.eni_overview
        args  = [eni_source_input.value]
      }
    }
  }

  container {
    width = 12
    table {
      title = "Source Subnet Table "
      query = query.network_interface
      args  = [eni_source_input.value]
    }
  }

  container {
    width = 12
    table {
      title = "Source Route Table"
      query = query.route
      args  = [subnet_source_input.value]
    }
  }

  container {
    width = 12
    table {
      title = "Source Route Table"
      query = query.route_table
      args  = [subnet_source_input.value]
    }
  }

  container {
    width = 12
    table {
      title = "Route Table Attachment"
      query = query.route_table_attachment
      args  = [route_table_source_input.value]
    }
  }

  container {
    width = 12
    table {
      title = "Source Routes"
      query = query.source_routes
      args  = [source_routes_input.value]
    }
  }

  container {
    width = 12
    table {
      title = "Source Transit Gateway"
      query = query.source_transit_gateway
      args  = [source_transit_gateway_input.value]
    }
  }

  container {
    width = 12
    table {
      title = "Transit Gateway Attachment"
      query = query.transit_gateway_attachment
      args  = [transit_gateway_attachment_input.value]
    }
  }

  category "catalog" {
    title = "catalog"
    icon  = "library-books"
    color = "orange"
  }
}

# Queries
query "source_routes" {
  sql = <<-EOQ
    SELECT destination_cidr_block
    FROM aws_all.aws_vpc_route
    WHERE transit_gateway_id IS NOT NULL
      AND destination_cidr_block::TEXT NOT LIKE 'pl%'
    ORDER BY destination_cidr_block::TEXT DESC;
  EOQ
}

query "source_transit_gateway" {
  sql = <<-EOQ
    SELECT transit_gateway_id, transit_gateway_owner_id, state
    FROM aws_all.aws_ec2_transit_gateway
    WHERE transit_gateway_id IN (
      SELECT DISTINCT transit_gateway_id
      FROM aws_all.aws_vpc_route
      WHERE route_table_id = $1
        AND transit_gateway_id IS NOT NULL
    );
  EOQ
  param "route_table_id" {}
}

query "transit_gateway_attachment" {
  sql = <<-EOQ
    SELECT transit_gateway_attachment_id, transit_gateway_id, state, transit_gateway_owner_id
    FROM aws_all.aws_ec2_transit_gateway_vpc_attachment
    WHERE transit_gateway_id = $1;
  EOQ
  param "transit_gateway_id" {}
}
