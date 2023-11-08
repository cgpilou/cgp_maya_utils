"""
TypeTool object library
"""

# imports third-parties
import maya.cmds
import maya.app.type.typeToolSetup

# import local
import cgp_maya_utils.constants
import cgp_maya_utils.scene


class TypeTool(cgp_maya_utils.scene.Transform):
    """TypeTool object that manipulates a ``TypeTool`` template
    """

    # OBJECT COMMANDS #

    @classmethod
    def create(cls,
               name=None,
               text=None,
               textAlignment=None,
               generatorMode=None,
               font=None,
               fontSize=None,
               fontStyle=None,
               isExtruded=False,
               **__):
        """create a typeTool

        :param name: the name of the typeTool
        :type name: str

        :param text: the text of the typeTool
        :type text: str

        :param textAlignment: the text alignment of the typeTool
        :type textAlignment: :class:`constants.TextAlignment`

        :param generatorMode: the generator mode of the typeTool
        :type generatorMode: :class:`constants.TypeGeneratorMode`

        :param font: the text font of the typeTool
        :type font: :class:`constants.Font`

        :param fontSize: the text font size of the typeTool
        :type fontSize: float

        :param fontStyle: the text font style of the typeTool
        :type fontStyle: :class:`constants.FontStyle`

        :param isExtruded: the text extrude state of the typeTool
        :type isExtruded: bool

        :return: the created typeTool object
        :rtype: :class:`TypeTool`
        """

        # init
        generatorMode = generatorMode or cgp_maya_utils.constants.TypeGeneratorMode.OFF
        textAlignment = textAlignment or cgp_maya_utils.constants.TextAlignment.LEFT
        fontStyle = fontStyle or cgp_maya_utils.constants.FontStyle.REGULAR
        font = font or cgp_maya_utils.constants.Font.LIBERATION_SANS
        fontSize = fontSize or 1
        text = text or 'set your own text'
        name = name or 'typeTool'

        # return if already existing
        if maya.cmds.objExists(name):
            return cls(name=name)

        # errors
        if generatorMode not in cgp_maya_utils.constants.TypeGeneratorMode.ALL:
            raise ValueError('{0} is a not a generator mode! Specify one : {1}'
                             .format(generatorMode, cgp_maya_utils.constants.TypeGeneratorMode.ALL))

        if textAlignment not in cgp_maya_utils.constants.TextAlignment.ALL:
            raise ValueError('{0} is a not a text alignment ! Specify one : {1}'
                             .format(textAlignment, cgp_maya_utils.constants.TextAlignment.ALL))

        if fontStyle not in cgp_maya_utils.constants.FontStyle.ALL:
            raise ValueError('{0} is a not style font ! Specify one : {1}'
                             .format(fontStyle, cgp_maya_utils.constants.FontStyle.ALL))

        if font not in cgp_maya_utils.constants.Font.ALL:
            raise ValueError('{0} is a not font ! Specify one : {1}'
                             .format(font, cgp_maya_utils.constants.Font.ALL))

        # create typeTool
        maya.app.type.typeToolSetup.createTypeTool()

        # instantiate object and rename
        typeTool = cls(maya.cmds.ls(sl=True)[0])
        typeTool.setName(name)

        # set text
        typeTool.setText(text=text,
                         generatorMode=generatorMode,
                         font=font,
                         fontStyle=fontStyle,
                         fontSize=fontSize,
                         alignment=textAlignment)

        # set extruded
        typeTool._typeExtrudeNode().attribute('enableExtrusion').setValue(isExtruded)

        # return
        return typeTool

    # COMMANDS #

    def data(self, worldSpace=False):
        """get the data necessary to store the transform and type node on disk and/or recreate it from scratch

        :param worldSpace: ``True`` : the transform values are queried in worldSpace -
                           ``False`` : the transform values are queried in local
        :type worldSpace: bool

        :return: the data of the transform and type node
        :rtype: dict
        """

        # init
        data = super(TypeTool, self).data()

        # get typeNode
        typeNode = self._typeNode()

        # update data
        data['text'] = self.text()
        data['textAlignment'] = typeNode.attribute('alignmentMode').value()
        data['generatorMode'] = typeNode.attribute('generator').value()
        data['font'] = typeNode.attribute('currentFont').value()
        data['fontSize'] = typeNode.attribute('fontSize').value()
        data['fontStyle'] = typeNode.attribute('currentStyle').value()
        data['isExtruded'] = typeNode.attribute('enableExtrusion').value()

        # return
        return data

    def setText(self, text=None, font=None, fontSize=None, fontStyle=None, alignment=None, generatorMode=None):
        """set the text of the typeTool

        :param text: the text of the typeTool
        :type text: str

        :param font: the font name of the text
        :type font: :class:`constants.Font`

        :param fontSize: the font size of the text
        :type fontSize: float

        :param fontStyle: the font style of the text
        :type fontStyle: :class:`constants.FontStyle`

        :param alignment: the alignment of the text
        :type alignment: :class:`constants.TextAlignment`

        :param generatorMode: the generator mode of the typeTool
        :type generatorMode: :class:`constants.TypeGeneratorMode`
        """

        # get typeNode
        typeNode = self._typeNode()

        # init
        text = text or self.text()
        generatorMode = generatorMode or typeNode.attribute('generator').value()
        alignment = alignment or typeNode.attribute('alignmentMode').value()
        font = font or typeNode.attribute('currentFont').value()
        fontStyle = fontStyle or typeNode.attribute('currentStyle').value()
        fontSize = fontSize or typeNode.attribute('fontSize').value()

        # errors
        if font not in cgp_maya_utils.constants.Font.ALL:
            raise ValueError('{0} is a not font ! Specify one : {1}'
                             .format(font, cgp_maya_utils.constants.Font.ALL))

        if fontStyle not in cgp_maya_utils.constants.FontStyle.ALL:
            raise ValueError('{0} is a not style font ! Specify one : {1}'
                             .format(fontStyle, cgp_maya_utils.constants.FontStyle.ALL))

        if alignment not in cgp_maya_utils.constants.TextAlignment.ALL:
            raise ValueError('{0} is a not a text alignment ! Specify one : {1}'
                             .format(alignment, cgp_maya_utils.constants.TextAlignment.ALL))

        if generatorMode not in cgp_maya_utils.constants.TypeGeneratorMode.ALL:
            raise ValueError('{0} is a not a generator mode! Specify one : {1}'
                             .format(generatorMode, cgp_maya_utils.constants.TypeGeneratorMode.ALL))

        # set font, font size, font style
        typeNode.attribute('currentFont').setValue(font)
        typeNode.attribute('fontSize').setValue(fontSize)
        typeNode.attribute('currentStyle').setValue(fontStyle)

        # set text alignment
        typeNode.attribute('alignmentMode').setValue(alignment)

        # set generator
        typeNode.attribute('generator').setValue(generatorMode)

        # set text when mode is off
        if generatorMode == cgp_maya_utils.constants.TypeGeneratorMode.OFF:

            # convert text
            convertedCharacters = ' '.join([character.encode(encoding='hex') for character in text])

            # set textInput
            typeNode.attribute('textInput').setValue(convertedCharacters)

        # set text when mode is python
        else:
            typeNode.attribute('pythonExpression').setValue(text)

    def text(self):
        """get the text input of the type node

        :return: the text input
        :rtype: str
        """

        # get typeNode
        typeNode = self._typeNode()

        # if generator mode is off
        if typeNode.attribute('generator').value() == cgp_maya_utils.constants.TypeGeneratorMode.OFF:

            # get input text
            inputText = typeNode.attribute('textInput').value().split(' ')

            # convert input text
            convertedCharacters = [character.decode(encoding='hex') for character in inputText]

            # return
            return ''.join(convertedCharacters)

        # if generator mode is python
        else:
            return typeNode.attribute('pythonExpression').value()

    # PRIVATE COMMANDS #

    def _typeExtrudeNode(self):
        """get the TypeExtrude node

        :return: the Type Extrude node
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # get the type extrude node
        typeExtrudeNode = maya.cmds.listConnections(self._typeNode(), type='typeExtrude')[0]

        # return
        return cgp_maya_utils.scene.Node(typeExtrudeNode)

    def _typeNode(self):
        """get the Type node

        :return: the Type node
        :rtype: :class:`cgp_maya_utils.scene.Node`
        """

        # get the type node
        typeNode = maya.cmds.listConnections(self.name(), type='type')[0]

        # return
        return cgp_maya_utils.scene.Node(typeNode)
