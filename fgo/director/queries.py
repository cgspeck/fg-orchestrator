import textwrap
import logging
import typing

from gql import gql

from fgo.director.agent_directory_settings import AgentDirectorySettings
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

def SetDirectoriesQuery(agent_directory_settings: AgentDirectorySettings):
    res_memo = 'ok error'
    logging.info(f'SetDirectoriesQuery agent_directory_settings: {agent_directory_settings}')

    def none_or_mutated_string(val: typing.Union[None, str]):
        if val is None:
            val = ""

        memo2 = val.replace('\\', '\\\\')
        return f'"{memo2}"'

    memo = textwrap.dedent(f'''\
        mutation {{
            flightgear_executable: setConfig(key: "fgfs_path", value: {none_or_mutated_string(agent_directory_settings.flightgear_executable)}) {{ {res_memo} }}
            fgroot_path: setConfig(key: "fgroot_path", value: {none_or_mutated_string(agent_directory_settings.fgroot_path)}) {{ {res_memo} }}
            fghome_path: setConfig(key: "fghome_path", value: {none_or_mutated_string(agent_directory_settings.fghome_path)}) {{ {res_memo} }}
            terrasync_path: setConfig(key: "terrasync_path", value: {none_or_mutated_string(agent_directory_settings.terrasync_path)}) {{ {res_memo} }}
            aircraft_path: setConfig(key: "aircraft_path", value: {none_or_mutated_string(agent_directory_settings.aircraft_path)}) {{ {res_memo} }}
        }}
    ''')

    logging.info(f'SetDirectoriesQuery about to send: \n\n\n{memo}')

    return gql(textwrap.dedent(memo))

# mutation {
#   startFlightGear(sessionArgs: {
#     aircraft: "Beechcraft-C18S"
#     aircraft_variant: "model18"
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
    memo = apply_string_if_not_none(memo, 'aircraftVariant', scenario_settings.aircraft_variant)
    # list containing strings
    memo = apply_value_if_not_none(memo, 'aiScenario', scenario_settings.ai_scenarios)

    if scenario_settings.selected_airport_option == 1:
        memo = apply_string_if_not_none(memo, 'airportCode', scenario_settings.airport)
    elif scenario_settings.selected_airport_option == 2:
        memo = apply_string_if_not_none(memo, 'carrier', scenario_settings.carrier)

    memo = apply_string_if_not_none(memo, 'ceiling', scenario_settings.ceiling)
    # bool 'true' or 'false'
    memo = apply_boolean_if_not_none(memo, 'enableAutoCoordination', scenario_settings.enable_auto_coordination)

    if scenario_settings.selected_runway_option == 1:
        memo = apply_string_if_not_none(memo, 'runway', scenario_settings.runway)
    elif scenario_settings.selected_runway_option == 2:
        memo = apply_string_if_not_none(memo, 'parkpos', scenario_settings.parking)

    memo = apply_string_if_not_none(memo, 'terrasyncHttpServer', scenario_settings.terra_sync_endpoint)
    # enum uppercase
    memo = apply_value_if_not_none(memo, 'timeOfDay', scenario_settings.time_of_day.upper())
    # integer
    memo = apply_value_if_not_none(memo, 'visibilityMeters', scenario_settings.visibility_in_meters)

    # THIS AGENT ONLY
    if custom_settings.additional_args is not None and len(custom_settings.additional_args) > 0:
        memo = apply_value_if_not_none(memo, 'additionalArgs', str(custom_settings.additional_args).replace("'", '"""'))

    memo = apply_boolean_if_not_none(memo, 'disableAi', custom_settings.disable_ai)
    memo = apply_boolean_if_not_none(memo, 'disableAiTraffic', custom_settings.disable_ai_traffic)
    memo = apply_boolean_if_not_none(memo, 'disableAntiAliasHud', custom_settings.disable_anti_alias_hud)
    memo = apply_boolean_if_not_none(memo, 'disableHud', custom_settings.disable_hud)
    memo = apply_boolean_if_not_none(memo, 'disablePanel', custom_settings.disable_panel)
    memo = apply_boolean_if_not_none(memo, 'disableSound', custom_settings.disable_sound)
    memo = apply_boolean_if_not_none(memo, 'enableClouds', custom_settings.enable_clouds)
    memo = apply_boolean_if_not_none(memo, 'enableClouds3d', custom_settings.enable_clouds3d)
    memo = apply_boolean_if_not_none(memo, 'enableFullscreen', custom_settings.enable_fullscreen)
    memo = apply_boolean_if_not_none(memo, 'enableTerrasync', custom_settings.enable_terrasync)
    memo = apply_boolean_if_not_none(memo, 'enableTelnetServer', custom_settings.enable_telnet_server)
    memo = apply_boolean_if_not_none(memo, 'enableRealWeatherFetch', custom_settings.enable_real_weather_fetch)
    memo = apply_boolean_if_not_none(memo, 'enableWebServer', custom_settings.enable_web_server)
    memo = apply_value_if_not_none(memo, 'fov', custom_settings.fov)
    memo = apply_value_if_not_none(memo, 'viewHeadingOffset', custom_settings.view_heading_offset)
    memo = apply_value_if_not_none(memo, 'viewPitchOffset', custom_settings.view_pitch_offset)
    # COMPUTED

    if hostname == scenario_settings.primary:
        # this is the primary!
        memo = apply_value_if_not_none(memo, 'role', 'PRIMARY')

        if scenario_settings.secondaries is not None:
            memo = apply_value_if_not_none(memo, 'clientIpAddresses', str(scenario_settings.secondaries).replace("'", '"'))
    else:
        # this is a secondary
        memo = apply_value_if_not_none(memo, 'role', 'SECONDARY')

    memo = wrapper % memo
    logging.info(f"StartFlightGear query for {hostname}:\n\n{memo}")
    return gql(memo)

def RemoteDirectoryListingQuery(remote_directory):
    return gql(textwrap.dedent(f'''
        {{
          directoryList(basePath: "{remote_directory}") {{
            basePath
            files
            directories
          }}
        }}
    '''))

