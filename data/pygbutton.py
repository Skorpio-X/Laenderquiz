"""
PygButton v0.1.0

PygButton (pronounced "pig button") is a module that implements UI buttons for
Pygame.
PygButton requires Pygame to be installed. Pygame can be downloaded from
http://pygame.org
PygButton was developed by Al Sweigart (al@inventwithpython.com)
https://github.com/asweigart/pygbutton


Simplified BSD License:

Copyright 2012 Al Sweigart. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Al Sweigart ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL Al Sweigart OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Al Sweigart.
"""

import os

import pygame
from pygame.locals import *


pygame.font.init()

# Need to copy this font from the pygame folder for the frozen version.
PYGBUTTON_FONT = pygame.font.Font('freesansbold.ttf', 14)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGRAY = (64, 64, 64)
GRAY = (128, 128, 128)
LIGHTGRAY = (212, 208, 200)


class PygButton(object):
    """Create a new button object.

    Parameters:
        rect - The size and position of the button as a pygame.Rect object
            or 4-tuple of integers.
        caption - The text on the button (default is blank)
        bgcolor - The background color of the button (default is a light
            gray color)
        fgcolor - The foreground color (i.e. the color of the text).
            Default is black.
        font - The pygame.font.Font object for the font of the text.
            Default is freesansbold in point 14.
        normal - A pygame.Surface object for the button's normal
            appearance.
        down - A pygame.Surface object for the button's pushed down
            appearance.
        highlight - A pygame.Surface object for the button's appearance
            when the mouse is over it.

    If the Surface objects are used, then the caption, bgcolor,
    fgcolor, and font parameters are ignored (and vice versa).
    Specifying the Surface objects lets the user use a custom image
    for the button.
    The normal, down, and highlight Surface objects must all be the
    same size as each other. Only the normal Surface object needs to
    be specified. The others, if left out, will default to the normal
    surface.
    """

    def __init__(self, rect=None, caption='', bgcolor=LIGHTGRAY, fgcolor=BLACK,
                 font=None, normal=None, down=None, highlight=None):
        if rect is None:
            self._rect = pygame.Rect(0, 0, 30, 60)
        else:
            self._rect = pygame.Rect(rect)

        self._caption = caption
        self._bgcolor = bgcolor
        self._fgcolor = fgcolor

        if font is None:
            self._font = PYGBUTTON_FONT
        else:
            self._font = font

        # tracks the state of the button
        self.buttonDown = False  # is the button currently pushed down?
        # is the mouse currently hovering over the button?
        self.mouseOverButton = False
        # was the last mouse down event over the mouse button? (Used to track
        # clicks.)
        self.lastMouseDownOverButton = False
        self._visible = True  # is the button visible
        # button starts as a text button instead of having custom images for
        # each surface
        self.customSurfaces = False

        if normal is None:
            # create the surfaces for a text button
            self.surfaceNormal = pygame.Surface(self._rect.size)
            self.surfaceDown = pygame.Surface(self._rect.size)
            self.surfaceHighlight = pygame.Surface(self._rect.size)
            self._update()  # draw the initial button images
        else:
            # create the surfaces for a custom image button
            self.set_surfaces(normal, down, highlight)

    def handle_event(self, event_obj):
        """All MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN event objects
        created by Pygame should be passed to this method. handle_event() will
        detect if the event is relevant to this button and change its state.

        There are two ways that your code can respond to button-events. One is
        to inherit the PygButton class and override the mouse*() methods. The
        other is to have the caller of handleEvent() check the return value
        for the strings 'enter', 'move', 'down', 'up', 'click', or 'exit'.

        Note that mouseEnter() is always called before mouseMove(), and
        mouseMove() is always called before mouseExit(). Also, mouseUp() is
        always called before mouseClick().

        buttonDown is always True when mouseDown() is called, and always False
        when mouseUp() or mouseClick() is called. lastMouseDownOverButton is
        always False when mouseUp() or mouseClick() is called.

        Parameters:
            event_obj
        """

        if (event_obj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN)
            or not self._visible):
            # The button only cares bout mouse-related events (or no events, if
            # it is invisible)
            return []

        ret_val = []

        has_exited = False
        if not self.mouseOverButton and self._rect.collidepoint(event_obj.pos):
            # if mouse has entered the button:
            self.mouseOverButton = True
            self.mouse_enter(event_obj)
            ret_val.append('enter')
        elif (self.mouseOverButton
              and not self._rect.collidepoint(event_obj.pos)):
            # if mouse has exited the button:
            self.mouseOverButton = False
            # call mouseExit() later, since we want mouseMove() to be handled
            # before mouseExit()
            has_exited = True

        if self._rect.collidepoint(event_obj.pos):
            # if mouse event happened over the button:
            if event_obj.type == MOUSEMOTION:
                self.mouse_move(event_obj)
                ret_val.append('move')
            elif event_obj.type == MOUSEBUTTONDOWN:
                self.buttonDown = True
                self.lastMouseDownOverButton = True
                self.mouse_down(event_obj)
                ret_val.append('down')
        else:
            if event_obj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # if an up/down happens off the button, then the next up won't
                # cause mouseClick()
                self.lastMouseDownOverButton = False

        # mouse up is handled whether or not it was over the button
        do_mouse_click = False
        if event_obj.type == MOUSEBUTTONUP:
            if self.lastMouseDownOverButton:
                do_mouse_click = True
            self.lastMouseDownOverButton = False

            if self.buttonDown:
                self.buttonDown = False
                self.mouse_up(event_obj)
                ret_val.append('up')

            if do_mouse_click:
                self.buttonDown = False
                self.mouse_click(event_obj)
                ret_val.append('click')

        if has_exited:
            self.mouse_exit(event_obj)
            ret_val.append('exit')

        return ret_val

    def draw(self, surface_obj):
        """Blit the current button's appearance to the surface object.

        Parameters:
            surface_obj (pygame.Surface)
        """
        if self._visible:
            if self.buttonDown:
                surface_obj.blit(self.surfaceDown, self._rect)
            elif self.mouseOverButton:
                surface_obj.blit(self.surfaceHighlight, self._rect)
            else:
                surface_obj.blit(self.surfaceNormal, self._rect)

    def _update(self):
        """Redraw the button's Surface object.

        Call this method when the button has changed appearance.
        """
        if self.customSurfaces:
            self.surfaceNormal = pygame.transform.smoothscale(
                self.origSurfaceNormal, self._rect.size)
            self.surfaceDown = pygame.transform.smoothscale(
                self.origSurfaceDown, self._rect.size)
            self.surfaceHighlight = pygame.transform.smoothscale(
                self.origSurfaceHighlight, self._rect.size)
            return

        w = self._rect.width  # syntactic sugar
        h = self._rect.height  # syntactic sugar

        # fill background color for all buttons
        self.surfaceNormal.fill(self.bgcolor)
        self.surfaceDown.fill(self.bgcolor)
        self.surfaceHighlight.fill(self.bgcolor)

        # draw caption text for all buttons
        caption_surf = self._font.render(self._caption, True, self.fgcolor,
                                         self.bgcolor)
        caption_rect = caption_surf.get_rect()
        caption_rect.center = int(w / 2), int(h / 2)
        self.surfaceNormal.blit(caption_surf, caption_rect)
        self.surfaceDown.blit(caption_surf, caption_rect)

        # draw border for normal button
        pygame.draw.rect(self.surfaceNormal, BLACK, pygame.Rect((0, 0, w, h)),
                         1)  # black border around everything
        pygame.draw.line(self.surfaceNormal, WHITE, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceNormal, WHITE, (1, 1), (1, h - 2))
        pygame.draw.line(self.surfaceNormal, DARKGRAY, (1, h - 1),
                         (w - 1, h - 1))
        pygame.draw.line(self.surfaceNormal, DARKGRAY, (w - 1, 1),
                         (w - 1, h - 1))
        pygame.draw.line(self.surfaceNormal, GRAY, (2, h - 2), (w - 2, h - 2))
        pygame.draw.line(self.surfaceNormal, GRAY, (w - 2, 2), (w - 2, h - 2))

        # draw border for down button.
        # black border around everything
        pygame.draw.rect(self.surfaceDown, BLACK, pygame.Rect((0, 0, w, h)), 1)
        pygame.draw.line(self.surfaceDown, WHITE, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceDown, WHITE, (1, 1), (1, h - 2))
        pygame.draw.line(self.surfaceDown, DARKGRAY, (1, h - 2), (1, 1))
        pygame.draw.line(self.surfaceDown, DARKGRAY, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceDown, GRAY, (2, h - 3), (2, 2))
        pygame.draw.line(self.surfaceDown, GRAY, (2, 2), (w - 3, 2))

        # draw border for highlight button
        self.surfaceHighlight = self.surfaceNormal

    def mouse_click(self, event):
        pass  # This class is meant to be overridden.

    def mouse_enter(self, event):
        pass  # This class is meant to be overridden.

    def mouse_move(self, event):
        pass  # This class is meant to be overridden.

    def mouse_exit(self, event):
        pass  # This class is meant to be overridden.

    def mouse_down(self, event):
        pass  # This class is meant to be overridden.

    def mouse_up(self, event):
        pass  # This class is meant to be overridden.

    def set_surfaces(self, normal_surface, down_surface=None,
                     highlight_surface=None):
        """Switch the button to a custom image type of button (rather than a
        text button). You can specify either a pygame.Surface object or a
        string of a filename to load for each of the three button appearance
        states.

        Parameters:
            normal_surface
            down_surface
            highlight_surface
        """
        if down_surface is None:
            down_surface = normal_surface
        if highlight_surface is None:
            highlight_surface = normal_surface

        if type(normal_surface) == str:
            self.origSurfaceNormal = pygame.image.load(normal_surface)
        if type(down_surface) == str:
            self.origSurfaceDown = pygame.image.load(down_surface)
        if type(highlight_surface) == str:
            self.origSurfaceHighlight = pygame.image.load(highlight_surface)

        if (self.origSurfaceNormal.get_size() !=
                self.origSurfaceDown.get_size() !=
                self.origSurfaceHighlight.get_size()):
            raise Exception('foo')

        self.surfaceNormal = self.origSurfaceNormal
        self.surfaceDown = self.origSurfaceDown
        self.surfaceHighlight = self.origSurfaceHighlight
        self.customSurfaces = True
        self._rect = pygame.Rect((self._rect.left,
                                  self._rect.top,
                                  self.surfaceNormal.get_width(),
                                  self.surfaceNormal.get_height()))

    def _prop_get_caption(self):
        return self._caption

    def _prop_set_caption(self, caption_text):
        self.customSurfaces = False
        self._caption = caption_text
        self._update()

    def _prop_get_rect(self):
        return self._rect

    def _prop_set_rect(self, new_rect):
        # Note that changing the attributes of the Rect won't update the
        # button. You have to re-assign the rect member.
        self._update()
        self._rect = new_rect

    def _prop_get_visible(self):
        return self._visible

    def _prop_set_visible(self, setting):
        self._visible = setting

    def _prop_get_fg_color(self):
        return self._fgcolor

    def _prop_set_fg_color(self, setting):
        self.customSurfaces = False
        self._fgcolor = setting
        self._update()

    def _prop_get_bg_color(self):
        return self._bgcolor

    def _prop_set_bg_color(self, setting):
        self.customSurfaces = False
        self._bgcolor = setting
        self._update()

    def _prop_get_font(self):
        return self._font

    def _prop_set_font(self, setting):
        self.customSurfaces = False
        self._font = setting
        self._update()

    caption = property(_prop_get_caption, _prop_set_caption)
    rect = property(_prop_get_rect, _prop_set_rect)
    visible = property(_prop_get_visible, _prop_set_visible)
    fgcolor = property(_prop_get_fg_color, _prop_set_fg_color)
    bgcolor = property(_prop_get_bg_color, _prop_set_bg_color)
    font = property(_prop_get_font, _prop_set_font)
