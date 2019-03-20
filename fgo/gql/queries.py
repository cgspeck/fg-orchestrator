import typing

from gql import gql

from fgo.director.scenario_settings import ScenarioSettings
from fgo.director.custom_agent_settings import CustomAgentSettings

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
        status
        uuid
        os
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

VERSION = gql('''
{  
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

def AircraftInstallQuery(aircraft):
  return gql(f'''mutation {{
    installOrUpdateAircraft(svnName: "{aircraft}") {{
      ok
      error
    }}
  }}
  ''')

def StartFlightGear(hostname, custom_settings, scenario_settings):
  pass
