**What is InfiniHexMonkey?**


Have you ever heard the saying "If you give a monkey a typewriter he will eventually write Shakespeare"?

Well this simple piece of software utilizes this concept to create ANY piece of software or file without the need to know how to code!!!!
Buttttt theres a catch...it may take forever and you may never create anything

If you give a monkey the ability to append hex randomly forever....he may be able to recreate Windows 11.

<img width="320" height="180" alt="image" src="https://github.com/user-attachments/assets/64da7ffd-a4fa-4b47-bf24-70d944fe2dbc" />



**How Does this Stupid Concept Work?**

Every file on your computer needs to be indentified somehow. These are called "header values" or "magic numnbers" Refer to: https://pinpointlabs.com/what-are-file-headers-signatures/'

By appending the hexadecimal header of the file you would like to create. Then we append a random number and value of hex bytes. Finally we append the end header of the file so the end. Essentially just making a giant file sandwich!

                    ---------------|
                    HEADER         |
                    RANDOM BYTES - |----File
                    END HEADER     |
                    ---------------|

By doing this you may be able to just one day randomly create a usable file!

By attempting to create an Archive file (e.g. Zip) and append a random number of bytes. Theoretically you would be able to eventually randomly create a zip archive with all of the required files to run Windows 11.
The odds of this happening? I dont know, I don't want to do the math but very its very low.

**How Do I Use This?**

Use "python3 InfiniHexMonkey.py"

<img width="297" height="392" alt="image" src="https://github.com/user-attachments/assets/5fe28f81-87ae-47ff-849c-ebb9ec85fffd" />

MAKE SURE YOU HAVE PILLOW INSTALLED!

Enter the hexadecimal for the file header and end header and then let the Monkey type away!

The included CSV file includes all of the valid hexadecimal bytes (0-255).
This CSV can be modified to include other strings in hexadecimal format to be appended randomly as well, hence why I went with this approach!

<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:param name="max" select="100000000"/>

  <xsl:template name="bounded-loop">
    <xsl:param name="n" select="$max"/>
    <xsl:if test="$n &gt; 0">
      <xsl:text>depth: </xsl:text>
      <xsl:value-of select="$n"/>
      <xsl:text>
</xsl:text>
      <xsl:call-template name="bounded-loop">
        <xsl:with-param name="n" select="$n - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template match="/">
    <!-- call with initial depth; change $max or pass parameter to control length -->
    <xsl:call-template name="bounded-loop">
      <xsl:with-param name="n" select="$max"/>
    </xsl:call-template>
  </xsl:template>

</xsl:stylesheet>

