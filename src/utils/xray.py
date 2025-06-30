import urllib.parse
from typing import List

from src.inbounds.schemas import InboundSecurity


def generate_vless_config(
    address: str,
    port: str,
    uuid: str,
    host: str,
    sni: str,
    fp: str,
    path: str,
    security: str,
    remark: str,
    sid: str,
    spx: str,
    pbk: str,
    flow: str = "",
    network_type: str = "ws",
    alpns: List[str] = None,
    mode: str = "",
    extra: str = "",
):
    prefix_txt = "%s@%s:%s" % (uuid, address, port)
    prefix = "vless://" + prefix_txt
    postfix_list = []

    postfix_list.append("encryption=%s" % "none")

    if flow:
        postfix_list.append("flow=%s" % flow)

    postfix_list.append("security=%s" % security)

    if sni:
        postfix_list.append("sni=%s" % sni)

    if alpns:
        alpns_str = ",".join(alpns)
        if alpns_str:
            postfix_list.append("alpn=%s" % urllib.parse.quote(alpns_str.encode("utf8")))

    postfix_list.append("fp=%s" % fp)

    postfix_list.append("type=%s" % network_type)

    if host:
        postfix_list.append("host=%s" % host)
        postfix_list.append("headerType=%s" % "http")

    postfix_list.append("path=%s" % urllib.parse.quote(path.encode("utf8")))

    if security == InboundSecurity.reality.value:
        if sid:
            postfix_list.append("sid=%s" % sid)
        if pbk:
            postfix_list.append("pbk=%s" % pbk)
        if spx:
            postfix_list.append("spx=%s" % urllib.parse.quote(spx.encode("utf8")))
    if network_type == "xhttp":
        postfix_list.append("mode=%s" % mode)
        if extra:
            postfix_list.append("extra=%s" % urllib.parse.quote(extra.encode("utf8")))
    link = (
        prefix
        + "?"
        + "&".join(postfix_list)
        + "#"
        + urllib.parse.quote(remark.encode("utf8"))
    )
    return link
