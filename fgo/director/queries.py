import textwrap
import logging
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
RESCAN_ENVIRONMENT = gql('''
mutation {
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
    return gql(textwrap.dedent(f'''
        mutation {{
          installOrUpdateAircraft(svnName: "{aircraft}") {{
            ok
            error
          }}
        }}
    '''))


# mutation {
#   startFlightGear(sessionArgs: {
#     aircraft: "c172p"
#     timeOfDay: NOON
#   }) {
#     assembledArgs
#     ok
#     error
#   }
# }
def StartFlightGear(hostname, scenario_settings: ScenarioSettings, custom_settings: CustomAgentSettings):
    '''
    Merges the CustomSettings, ScenarioSettings for given hostname and
    provides a query to start FlightGear.
    '''
    wrapper = textwrap.dedent(f'''
        mutation {{
            startFlightGear(sessionArgs: {{
                %s
            }}) {{
                assembledArgs
                ok
                error
            }}
        }}
    ''')

    memo = ''

    def apply_string_if_not_none(memo, gql_key, value):
        ''' Wraps value in gql/js compliant quotes '''
        if value is not None:
            memo += f'            {gql_key}: "{value}"\n'

        return memo

    def apply_boolean_if_not_none(memo, gql_key, value):
        ''' Converts value to gql/js compliant true/false '''
        if value is not None:
            memo += f'            {gql_key}: {"true" if value else "false"}\n'

        return memo

    def apply_value_if_not_none(memo, gql_key, value):
        ''' Applies value as is '''
        if value is not None:
            memo += f'            {gql_key}: {value}\n'

        return memo

    # COMMON TO SCENARIO
    memo = apply_string_if_not_none(memo, 'aircraft', scenario_settings.aircraft)
    # list containing strings
    memo = apply_value_if_not_none(memo, 'aiScenario', scenario_settings.ai_scenarios)
    memo = apply_string_if_not_none(memo, 'carrier', scenario_settings.carrier)
    memo = apply_string_if_not_none(memo, 'airportCode', scenario_settings.airport)
    memo = apply_string_if_not_none(memo, 'ceiling', scenario_settings.ceiling)
    # bool 'true' or 'false'
    memo = apply_boolean_if_not_none(memo, 'enableAutoCoordination', scenario_settings.enable_auto_coordination)
    memo = apply_string_if_not_none(memo, 'runway', scenario_settings.runway)
    memo = apply_string_if_not_none(memo, 'terrasyncHttpServer', scenario_settings.terra_sync_endpoint)
    # enum uppercase
    memo = apply_value_if_not_none(memo, 'timeOfDay', scenario_settings.time_of_day.upper())
    # integer
    memo = apply_value_if_not_none(memo, 'visibilityMeters', scenario_settings.visibility_in_meters)

    # THIS AGENT ONLY
    memo = apply_value_if_not_none(memo, 'additionalArgs', custom_settings.additional_args)
    memo = apply_boolean_if_not_none(memo, 'disablePanel', custom_settings.disable_panel)
    memo = apply_boolean_if_not_none(memo, 'disableHud', custom_settings.disable_hud)
    memo = apply_boolean_if_not_none(memo, 'disableAntiAliasHud', custom_settings.disable_anti_alias_hud)
    memo = apply_boolean_if_not_none(memo, 'enableClouds', custom_settings.enable_clouds)
    memo = apply_boolean_if_not_none(memo, 'enableClouds3d', custom_settings.enable_clouds3d)
    memo = apply_boolean_if_not_none(memo, 'enableFullscreen', custom_settings.enable_fullscreen)
    memo = apply_boolean_if_not_none(memo, 'enableTerrasync', custom_settings.enable_terrasync)
    memo = apply_boolean_if_not_none(memo, 'enableRealWeatherFetch', custom_settings.enable_real_weather_fetch)
    memo = apply_value_if_not_none(memo, 'fov', custom_settings.fov)
    memo = apply_value_if_not_none(memo, 'viewOffset', custom_settings.view_offset)
    # COMPUTED

    if hostname == scenario_settings.master:
        # this is the master!
        memo = apply_value_if_not_none(memo, 'role', 'MASTER')
        memo = apply_value_if_not_none(memo, 'clientIpAddresses', scenario_settings.slaves)
    else:
        # this is a slave
        memo = apply_value_if_not_none(memo, 'role', 'SLAVE')

    memo = wrapper % memo
    logging.info(f"StartFlightGear query for {hostname}:\n\n{memo}")
    return gql(memo)
