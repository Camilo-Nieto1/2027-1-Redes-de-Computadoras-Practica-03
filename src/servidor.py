"""Docstring."""
import socket
import json
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6700
DNS = "8.8.8.8"
SUBNET = "255.255.255.0"

def iniciar_servidor():
    """Hey."""
    disponibles = {"127.0.0.2","127.0.0.3","127.0.0.4","127.0.0.5"}
    ocupadas = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_HOST, SERVER_PORT))
    print(f"[*] Servidor DHCP escuchando en {SERVER_HOST}:{SERVER_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        mensaje = json.loads(data.decode("utf-8"))
        if mensaje.get("type") == "DHCPDISCOVER":
            offer(data,addr,mensaje,disponibles,sock)
        elif mensaje.get("type") == "DHCPREQUEST":
            # TODO : Confirmar asignacion y responder con DHCPACK
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
                offer(data,addr,mensaje,disponibles,sock)


def offer(data,addr,mensaje,disponibles,sock):
    print(f"[*]DISCOVERrecibidodeMAC:{mensaje['mac']}")
    # Decodificamos datos y recuperamos json
    parsed_data = json.loads(data.decode('utf-8'))
    xid = parsed_data.get("xid")
    if(len(disponibles)):
        # obtenemos una dirección
        propuesta = disponibles.pop()
        disponibles.add(propuesta)
        #Enviamos la propuesta
        offer_msg = {"type": "DHCPOFFER",
                     "xid": xid,
                     "offered_ip": propuesta,
                     "subnet": SUBNET,
                     "dns": DNS}
                
        sock.sendto(json.dumps(offer_msg).encode("utf8"),
                    addr)
if __name__ == "__main__":
    iniciar_servidor()
