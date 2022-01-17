import argparse
from multiprocessing import Process

from common import DEFAULT_SERVER_ADDR, client_ai_teaming, pairing_clients
from network import Server
from tasks.affective_task import (INDIVIDUAL_IMAGE_TIMER,
                                  INDIVIDUAL_RATING_TIMER, TEAM_IMAGE_TIMER,
                                  TEAM_RATING_TIMER, ServerAffectiveTask)
from tasks.finger_tapping_task import ServerFingerTappingTask
from tasks.ping_pong_task import ServerPingPongTask


def run_ping_pong(to_client_connections: list, from_client_connections: dict, session_name: str, easy_mode: bool = True):
    server_ping_pong_task = ServerPingPongTask(to_client_connections, 
                                               from_client_connections,
                                               easy_mode=easy_mode,
                                               session_name=session_name)
    server_ping_pong_task.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run server of finger tapping task.')
    parser.add_argument("-a", "--address", metavar='', help="IP address of server")
    parser.add_argument("-p", "--port", type=int, required=True, metavar='', help="Port of server")
    args = parser.parse_args()

    server_address = DEFAULT_SERVER_ADDR if args.address is None else args.address
    server_port = args.port

    server = Server(server_address, server_port)

    server.establish_connections()

    # # Finger tapping task
    # server_finger_tapping_task = ServerFingerTappingTask(list(server.to_client_connections.values()), 
    #                                                      server.from_client_connections)
    # server_finger_tapping_task.run()

    # server.establish_connections()

    # Affective task
    server_affective_task = ServerAffectiveTask(list(server.to_client_connections.values()), 
                                                     server.from_client_connections)
    
    # Individual
    server_affective_task.run("./tasks/affective_task/images/task_images", 
                              INDIVIDUAL_IMAGE_TIMER, 
                              INDIVIDUAL_RATING_TIMER, 
                              collaboration=False)

    server.establish_connections()

    # Team
    server_affective_task.run("./tasks/affective_task/images/task_images", 
                              TEAM_IMAGE_TIMER, 
                              TEAM_RATING_TIMER, 
                              collaboration=True)

    server.establish_connections()

    # # Ping pong competitive
    # client_pairs = pairing_clients(server.to_client_connections, server.from_client_connections)

    # ping_pong_processes = []
    # for session_id, (to_client_connection_pair, from_client_connection_pair) in enumerate(client_pairs):
    #     to_client_connections = []
    #     for to_client_connection_team in to_client_connection_pair:
    #         to_client_connections = to_client_connections + list(to_client_connection_team.values())

    #     session_name = "competitive_" + str(session_id)
    #     process = Process(target=run_ping_pong, args=(to_client_connections, from_client_connection_pair, session_name))
    #     ping_pong_processes.append(process)

    # for process in ping_pong_processes:
    #     process.start()
    
    # for process in ping_pong_processes:
    #     process.join()

    # server.establish_connections()

    # # Ping pong cooperative
    # client_pairs = client_ai_teaming(server.to_client_connections, server.from_client_connections)

    # ping_pong_processes = []
    # for session_id, (to_client_connection_teams, from_client_connection_teams) in enumerate(client_pairs):
    #     to_client_connections = []
    #     for to_client_connection_team in to_client_connection_teams:
    #         to_client_connections = to_client_connections + list(to_client_connection_team.values())

    #     session_name = "cooperative_" + str(session_id)
    #     process = Process(target=run_ping_pong, args=(to_client_connections, from_client_connection_teams, session_name, False))
    #     ping_pong_processes.append(process)

    # for process in ping_pong_processes:
    #     process.start()

    # for process in ping_pong_processes:
    #     process.join()

    # server.establish_connections()
