import re
import logging
import networkx as nx
from selenium.common.exceptions import NoSuchElementException
from util.concept_map.common import get_latest_concept_map
from util.config import JAVADOC_GLOBAL_NAME
from util.constant import *


# javadoc所有module和package的名字，为了兼容java8之前不带module的url和之后带module的url
javadoc_module_and_packages = set(['java.base', 'java.compiler', 'java.datatransfer', 'java.desktop', 'java.instrument', 'java.logging', 'java.management', 'java.management.rmi', 'java.naming', 'java.net.http', 'java.prefs', 'java.rmi', 'java.scripting', 'java.se', 'java.security.jgss', 'java.security.sasl', 'java.smartcardio', 'java.sql', 'java.sql.rowset', 'java.transaction.xa', 'java.xml', 'java.xml.crypto', 'jdk.accessibility', 'jdk.attach', 'jdk.charsets', 'jdk.compiler', 'jdk.crypto.cryptoki', 'jdk.crypto.ec', 'jdk.dynalink', 'jdk.editpad', 'jdk.hotspot.agent', 'jdk.httpserver', 'jdk.incubator.foreign', 'jdk.incubator.jpackage', 'jdk.jartool', 'jdk.javadoc', 'jdk.jcmd', 'jdk.jconsole', 'jdk.jdeps', 'jdk.jdi', 'jdk.jdwp.agent', 'jdk.jfr', 'jdk.jlink', 'jdk.jshell', 'jdk.jsobject', 'jdk.jstatd', 'jdk.localedata', 'jdk.management', 'jdk.management.agent', 'jdk.management.jfr', 'jdk.naming.dns', 'jdk.naming.rmi', 'jdk.net', 'jdk.rmic', 'jdk.scripting.nashorn', 'jdk.sctp', 'jdk.security.auth', 'jdk.security.jgss', 'jdk.xml.dom', 'jdk.zipfs', 'java.io', 'java.lang', 'java.lang.annotation', 'java.lang.constant', 'java.lang.invoke', 'java.lang.module', 'java.lang.ref', 'java.lang.reflect', 'java.lang.runtime', 'java.math', 'java.net', 'java.net.spi', 'java.nio', 'java.nio.channels', 'java.nio.channels.spi', 'java.nio.charset', 'java.nio.charset.spi', 'java.nio.file', 'java.nio.file.attribute', 'java.nio.file.spi', 'java.security', 'java.security.cert', 'java.security.interfaces', 'java.security.spec', 'java.text', 'java.text.spi', 'java.time', 'java.time.chrono', 'java.time.format', 'java.time.temporal', 'java.time.zone', 'java.util', 'java.util.concurrent', 'java.util.concurrent.atomic', 'java.util.concurrent.locks', 'java.util.function', 'java.util.jar', 'java.util.regex', 'java.util.spi', 'java.util.stream', 'java.util.zip', 'javax.crypto', 'javax.crypto.interfaces', 'javax.crypto.spec', 'javax.net', 'javax.net.ssl', 'javax.security.auth', 'javax.security.auth.callback', 'javax.security.auth.login', 'javax.security.auth.spi', 'javax.security.auth.x500', 'javax.security.cert', 'javax.annotation.processing', 'javax.lang.model', 'javax.lang.model.element', 'javax.lang.model.type', 'javax.lang.model.util', 'javax.tools', 'java.awt.datatransfer', 'java.applet', 'java.awt', 'java.awt.color', 'java.awt.desktop', 'java.awt.dnd', 'java.awt.event', 'java.awt.font', 'java.awt.geom', 'java.awt.im', 'java.awt.im.spi', 'java.awt.image', 'java.awt.image.renderable', 'java.awt.print', 'java.beans', 'java.beans.beancontext', 'javax.accessibility', 'javax.imageio', 'javax.imageio.event', 'javax.imageio.metadata', 'javax.imageio.plugins.bmp', 'javax.imageio.plugins.jpeg', 'javax.imageio.plugins.tiff', 'javax.imageio.spi', 'javax.imageio.stream', 'javax.print', 'javax.print.attribute', 'javax.print.attribute.standard', 'javax.print.event', 'javax.sound.midi', 'javax.sound.midi.spi', 'javax.sound.sampled',
                                   'javax.sound.sampled.spi', 'javax.swing', 'javax.swing.border', 'javax.swing.colorchooser', 'javax.swing.event', 'javax.swing.filechooser', 'javax.swing.plaf', 'javax.swing.plaf.basic', 'javax.swing.plaf.metal', 'javax.swing.plaf.multi', 'javax.swing.plaf.nimbus', 'javax.swing.plaf.synth', 'javax.swing.table', 'javax.swing.text', 'javax.swing.text.html', 'javax.swing.text.html.parser', 'javax.swing.text.rtf', 'javax.swing.tree', 'javax.swing.undo', 'java.lang.instrument', 'java.util.logging', 'java.lang.management', 'javax.management', 'javax.management.loading', 'javax.management.modelmbean', 'javax.management.monitor', 'javax.management.openmbean', 'javax.management.relation', 'javax.management.remote', 'javax.management.timer', 'javax.management.remote.rmi', 'javax.naming', 'javax.naming.directory', 'javax.naming.event', 'javax.naming.ldap', 'javax.naming.ldap.spi', 'javax.naming.spi', 'java.util.prefs', 'java.rmi.activation', 'java.rmi.dgc', 'java.rmi.registry', 'java.rmi.server', 'javax.rmi.ssl', 'javax.script', 'javax.security.auth.kerberos', 'org.ietf.jgss', 'javax.security.sasl', 'javax.smartcardio', 'javax.sql', 'javax.sql.rowset', 'javax.sql.rowset.serial', 'javax.sql.rowset.spi', 'javax.transaction.xa', 'javax.xml', 'javax.xml.catalog', 'javax.xml.datatype', 'javax.xml.namespace', 'javax.xml.parsers', 'javax.xml.stream', 'javax.xml.stream.events', 'javax.xml.stream.util', 'javax.xml.transform', 'javax.xml.transform.dom', 'javax.xml.transform.sax', 'javax.xml.transform.stax', 'javax.xml.transform.stream', 'javax.xml.validation', 'javax.xml.xpath', 'org.w3c.dom', 'org.w3c.dom.bootstrap', 'org.w3c.dom.events', 'org.w3c.dom.ls', 'org.w3c.dom.ranges', 'org.w3c.dom.traversal', 'org.w3c.dom.views', 'org.xml.sax', 'org.xml.sax.ext', 'org.xml.sax.helpers', 'javax.xml.crypto', 'javax.xml.crypto.dom', 'javax.xml.crypto.dsig', 'javax.xml.crypto.dsig.dom', 'javax.xml.crypto.dsig.keyinfo', 'javax.xml.crypto.dsig.spec', 'com.sun.java.accessibility.util', 'com.sun.tools.attach', 'com.sun.tools.attach.spi', 'com.sun.source.doctree', 'com.sun.source.tree', 'com.sun.source.util', 'com.sun.tools.javac', 'jdk.dynalink.beans', 'jdk.dynalink.linker', 'jdk.dynalink.linker.support', 'jdk.dynalink.support', 'com.sun.net.httpserver', 'com.sun.net.httpserver.spi', 'com.sun.jarsigner', 'jdk.security.jarsigner', 'jdk.javadoc.doclet', 'com.sun.tools.jconsole', 'com.sun.jdi', 'com.sun.jdi.connect', 'com.sun.jdi.connect.spi', 'com.sun.jdi.event', 'com.sun.jdi.request', 'jdk.jfr.consumer', 'jdk.jshell.execution', 'jdk.jshell.spi', 'jdk.jshell.tool', 'netscape.javascript', 'com.sun.management', 'jdk.nio', 'jdk.nashorn.api.scripting', 'jdk.nashorn.api.tree', 'com.sun.nio.sctp', 'com.sun.security.auth', 'com.sun.security.auth.callback', 'com.sun.security.auth.login', 'com.sun.security.auth.module', 'com.sun.security.jgss', 'org.w3c.dom.css', 'org.w3c.dom.html', 'org.w3c.dom.stylesheets', 'org.w3c.dom.xpath'])


def get_api_path_from_href(href, target_doc: str = JAVADOC_GLOBAL_NAME):
    '''
    去除超链接中的冗余内容，获取每个超链接对应的API链接
    与concept map中的包不同的地方在于把api的前缀也识别出来了
    '''
    ret = ''
    patterns = {
        JAVADOC_GLOBAL_NAME: f'(?<=api/).*$'
    }
    try:
        match = re.search(patterns[target_doc], href)
    except Exception as e:
        return ret
    if match is not None:
        ret = match.group()
    else:
        ret = ''
    ret = ret.replace('%3C', '<')
    ret = ret.replace('%3E', '>')
    ret = ret.replace('%5B', '[')
    ret = ret.replace('%5D', ']')
    return ret


def api_url_match(url1: str, url2: str, target_doc=JAVADOC_GLOBAL_NAME):
    '''
    严格匹配两个url是不是指向同一个api
    '''
    api_path1 = get_api_path_from_href(url1, target_doc)
    api_path2 = get_api_path_from_href(url2, target_doc)
    # javadoc则要去除url中的module name再匹配
    if target_doc == JAVADOC_GLOBAL_NAME:
        api_components1 = [item for item in api_path1.split(
            '/') if item != '' and item not in javadoc_module_and_packages]
        api_components2 = [item for item in api_path2.split(
            '/') if item != '' and item not in javadoc_module_and_packages]
        api_path1 = '/'.join(api_components1).lower()
        api_path2 = '/'.join(api_components2).lower()
    return api_path1 == api_path2


def longest_common_subsequence(A: str, B: str) -> int:
    m, n = len(A), len(B)
    ans = 0
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if A[i - 1] == B[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            ans = max(ans, dp[i][j])
    return ans


def camel_case_split(str):
    if len(str) < 1:
        return []
    words = [[str[0]]]

    for c in str[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return [''.join(word).lower() for word in words]


def min_edit_distance(word1, word2):
    """
    :type word1: str
    :type word2: str
    :rtype: int
    """
    n = len(word1)
    m = len(word2)

    # 有一个字符串为空串
    if n * m == 0:
        return n + m

    # DP 数组
    D = [[0] * (m + 1) for _ in range(n + 1)]

    # 边界状态初始化
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j

    # 计算所有 DP 值
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            left = D[i - 1][j] + 1
            down = D[i][j - 1] + 1
            left_down = D[i - 1][j - 1]
            if word1[i - 1] != word2[j - 1]:
                left_down += 1
            D[i][j] = min(left, down, left_down)

    return D[n][m]


def get_api_name_from_entity_id(entity_id: str):
    '''
    concept map中API的ID经常带api和html等无用信息，所以就去掉一下
    '''
    return entity_id.replace('.html', '').replace('api/', '')
