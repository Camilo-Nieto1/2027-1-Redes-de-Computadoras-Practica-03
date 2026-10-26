"""Odio pep8."""
import socket
import json
import random


def iniciar_cliente(mac_address):
    """Pep_ocho."""
    idc = "cliente:",mac_address
    print(idc, "Inicia")
    cliente_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente_sock.settimeout(5.0)
    xid = random.randint(100000, 999999)
    direccion = None
    # 1. Enviar DHCPDISCOVER
    discover_msg = {"type": "DHCPDISCOVER", "mac": mac_address, "xid": xid}
    cliente_sock.sendto(json.dumps(discover_msg).encode("utf-8"), ("127.0.0.1", 6700))

    while direccion is None:
    # TODO : Esperar DHCPOFFER , enviar DHCPREQUEST y esperar DHCPACK
        data, addr = cliente_sock.recvfrom(1024)
        mensaje = json.loads(data.decode("utf-8"))
        print("cliente:",mac_address, "recibió", mensaje.get("type"))

        if mensaje.get("type") == "DHCPOFFER":
            # Decodificamos datos y recuperamos json
            propuesta = mensaje.get("offered_ip")
            
            # Aceptamos (pedimos) la dirección propuesta propuesta
            print("cliente:",mac_address, "pide", propuesta)
    
            accept_msg = {
                "type": "DHCPREQUEST",
                "mac": mac_address,
                "xid": xid,
                "requested_ip": propuesta}
            # Enviamos 
            cliente_sock.sendto(json.dumps(accept_msg).encode("utf-8"),
                                ("127.0.0.1", 6700))
        elif(mensaje.get("type") == "DHCPACK"):
            direccion = mensaje.get("assigned_ip")
            tiempo =  mensaje.get("lease_time")
            print(idc,
                  "obtuvo la direción", direccion,
                  "por", tiempo, "tiempo")
        else:
            continue


if __name__ == "__main__":
    # Dirección MAC aleatoria
    mac_address = ":".join(f"{b:02x}"
                           for b
                           in [random.randint(0, 255) for _ in range(6)])
    iniciar_cliente(mac_address)
    



    
