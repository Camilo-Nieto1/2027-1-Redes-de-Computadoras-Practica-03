"""Docstring."""
import socket
import json
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6700
DNS = "8.8.8.8"
SUBNET = "255.255.255.0"


def iniciar_servidor():
    """Función que inicia el servidor y espera asignaciones."""
    disponibles = {"127.0.0.2", "127.0.0.3", "127.0.0.4"}
    pendientes = {}  # mac:direccion_propuesta
    ocupadas = {}    # direcciones ocupadas
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_HOST, SERVER_PORT))
    print(f"[*] Servidor DHCP escuchando en {SERVER_HOST}:{SERVER_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        mensaje = json.loads(data.decode("utf-8"))
        if mensaje.get("type") == "DHCPDISCOVER":
            print(f"[*]DISCOVER recibido de MAC:{mensaje['mac']}")
            offer(addr, mensaje, disponibles, pendientes, sock)

        # Si se recibe DHCPREQUEST de un pendiente.
        elif (mensaje.get("type") == "DHCPREQUEST" and
              mensaje.get("mac") in pendientes and
              pendientes[(mensaje.get("mac"))] == mensaje.get("requested_ip")):
            # Confirmar asignacion y responder con DHCPACK
            print(f"[*]DHCPREQUEST válido recibido de MAC:{mensaje['mac']}")

            xid = mensaje.get("xid")
            pedida = mensaje.get("requested_ip")
            mac = mensaje.get("requested_ip")
            print(f"    se le asigna la dirección {pedida}")
            if (pedida in disponibles):
                disponibles.remove(pedida)
                ocupadas[pedida] = mac
                ack_msg = {
                    "type": "DHCPACK",
                    "xid": xid,
                    "assigned_ip": pedida,
                    "lease_time": 10}
                sock.sendto(json.dumps(ack_msg).encode("utf-8"),
                            addr)
            elif (mensaje.get("type") == "DHCPREQUEST" and
                  not (mensaje.get("mac") in pendientes)):
                print(f"[*]{mensaje.get('tipo')}",
                      f"recibido de MAC:{mensaje['mac']}\n"
                      "NO HAY DIRECCIÓN DISPONIBLE")
            else:
                # Enviamos otra oferta
                print(f"[*]{mensaje.get('type')} NO válido",
                      f"recibido de MAC:{mensaje.get('mac')}")
                print("    Se envía propuesta de dirección")
                offer(addr, mensaje, disponibles, pendientes, sock)
        else:
            print("No debería imprimirse esto... :o")
            print(f"[*]{mensaje.get('tipo')} NO válido",
                  f"recibido de MAC:{mensaje['mac']}")
            continue


def offer(addr, mensaje, disponibles, pendientes, sock):
    """Función que manda una oferta a de una dirección a un cliente."""
    xid = mensaje.get("xid")
    if (len(disponibles)):
        # obtenemos una dirección
        propuesta = next(iter(disponibles))
        # Pasamos mac a pendientes
        mac = mensaje.get("mac")
        pendientes[mac] = propuesta
        # Enviamos la propuesta
        offer_msg = {"type": "DHCPOFFER",
                     "xid": xid,
                     "offered_ip": propuesta,
                     "subnet": SUBNET,
                     "dns": DNS}
        # print(offer_msg)

        sock.sendto(json.dumps(offer_msg).encode("utf-8"),
                    addr)
    else:
        print("    NO HAY DIRECCIONES DISPONIBLES")


if __name__ == "__main__":
    iniciar_servidor()
