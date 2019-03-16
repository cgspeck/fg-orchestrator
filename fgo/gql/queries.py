from gql import gql

AIRCRAFT = gql('''
{
  info {
    aircraft {
      id
      name
      version
    }
  }
}
''')

AI_SCENARIOS = gql('''
{
  aiScenarios {
    id
    name
  }
}
''')

CONFIG = gql('''
{
  config {
    id
    key
    value
  }
}
''')

INFO = gql('''
{
    info {
        id
        status
        uuid
        os
        timestamp
        errors {
            id
            code
            description
        }
    }
    version {
        versionString
    }
}
''')

# mutations
RESCAN_ENVIRONMENT = gql('''mutation {
  rescanEnvironment {
    ok
  }
}''')

STOP_FLIGHTGEAR = gql('''mutation {
  stopFlightGear {
    ok
    error
  }
}''')