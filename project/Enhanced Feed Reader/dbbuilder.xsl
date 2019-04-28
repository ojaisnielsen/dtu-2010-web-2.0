<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:efr="EnhancedFeedReader"
    xmlns:set="http://exslt.org/sets">

    <xsl:output encoding="UTF-8"/>

    <xsl:param name="date"/>
    <xsl:param name="link"/>
    <xsl:param name="title"/>

    <xsl:template match="/html">
        <entry>
            <xsl:attribute name="title">
                <xsl:value-of select="$title"/>
            </xsl:attribute>
            <xsl:attribute name="link">
                <xsl:value-of select="$link"/>
            </xsl:attribute>   
            <xsl:attribute name="date">
                <xsl:value-of select="$date"/>
            </xsl:attribute>

            <head>

                <xsl:for-each select="set:distinct(//enamex[not(efr:getRealName(string(.)) = '')])">
                    <entity>
                        <xsl:attribute name="type">
                            <xsl:value-of select="@type"/>
                        </xsl:attribute>
                        <xsl:if test="@type = 'LOCATION'">
                            <xsl:attribute name="coordinates">
                                <xsl:value-of select="efr:getLocationCoordinates(efr:getRealName(string(.)))"/>
                            </xsl:attribute>
                        </xsl:if>
                        <xsl:value-of select="efr:getRealName(string(.))"/>
                    </entity>
                </xsl:for-each>
            </head>
            <xsl:apply-templates select="@*|node()"/>
        </entry>
    </xsl:template>

    <xsl:template match="@*|node()">
        <xsl:choose>
            <xsl:when test="name() = 'body'">
                <xsl:copy>
                    <xsl:apply-templates select="node()"/>
                </xsl:copy>
            </xsl:when>
            <xsl:when test="name() = 'enamex'">
                <span>
                    <xsl:attribute name="class">
                        <xsl:value-of select="concat('ENTITY ', @type)"/>
                    </xsl:attribute>
                    <xsl:attribute name="title">
                        <xsl:value-of select="efr:getRealName(string(.))"/>
                    </xsl:attribute>
                    <xsl:apply-templates select="node()"/>
                </span>
            </xsl:when>
            <xsl:when test="name() = 's'">
                <span class="SENTENCE">
                    <xsl:apply-templates select="node()"/>
                </span>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates select="@*|node()"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>

</xsl:stylesheet>