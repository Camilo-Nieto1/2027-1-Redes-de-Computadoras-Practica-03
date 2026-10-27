"""Docstring."""
import socket
import json
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6700
DNS = "8.8.8.8"
SUBNET = "255.255.255.0"

def iniciar_servidor():
    """Hey."""
    disponibles = {"127.0.0.2", "127.0.0.3", "127.0.0.4", "127.0.0.5"}
    pendientes = {} # mac (mensaje)
    ocupadas = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_HOST, SERVER_PORT))
    print(f"[*] Servidor DHCP escuchando en {SERVER_HOST}:{SERVER_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        mensaje = json.loads(data.decode("utf-8"))
        if mensaje.get("type") == "DHCPDISCOVER":
            offer(addr, mensaje, disponibles, pendientes, sock)

        # Si se recibe DHCPREQUEST de un pendiente.
        elif (mensaje.get("type") == "DHCPREQUEST" and
              mensaje.get("mac") in pendientes and
              pendientes[(mensaje.get("mac"))] == mensaje.get("requested_ip")):
            # Confirmar asignacion y responder con DHCPACK
            xid = mensaje.get("xid")
            pedida = mensaje.get("requested_ip")
            mac = mensaje.get("requested_ip")
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
            else:
                # Enviamos otra oferta
                offer(addr,mensaje,disponibles,pendientes,sock)
        else:
            continue

def offer(addr, mensaje, disponibles, pendientes, sock):
    print(f"[*]DISCOVERrecibidode MAC:{mensaje['mac']}")
    xid = mensaje.get("xid")
    if(len(disponibles)):
        # obtenemos una dirección
        propuesta = next(iter(disponibles))
        # Pasamos mac a pendientes
        mac = mensaje.get("mac")
        pendientes[mac] = propuesta
        #Enviamos la propuesta
        offer_msg = {"type": "DHCPOFFER",
                     "xid": xid,
                     "offered_ip": propuesta,
                     "subnet": SUBNET,
                     "dns": DNS}

        sock.sendto(json.dumps(offer_msg).encode("utf-8"),
                    addr)


if __name__ == "__main__":
    iniciar_servidor()
