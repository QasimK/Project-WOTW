'''
Created on 28 Jun 2011

@author: Qasim
'''

import string
import math as maths

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from game.views import game_action_resolver
from django.template.base import VariableDoesNotExist

register = template.Library()

def get_str(tag, tokenstr):
    """Return the string tokenstr without quotes
    
    TemplateSyntaxError is raised if there are not any quotes
    The tag name is required for any error message."""
    
    if not (tokenstr[0] == tokenstr[-1] and tokenstr[0] in ("'", '"')):
        err = "%s tag argument (%s) must be in quotes"%(tag, tokenstr)
        raise template.TemplateSyntaxError(err)
    return tokenstr[1:-1]


@register.tag(name="action_link")
def do_action_link(parser, token):
    """
    {% action_link "registered-action" "display text" "varname" varvalue %}
    
    varvalue can be a variable.
    You can have many variables.
    """
    try:
        sep = token.split_contents()
        tag_name = sep[0]
        action_name = sep[1]
        url_text = sep[2]
        remaining = sep[3:]
    except ValueError:
        err = "%s tag requires at least 3 arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError(err)
    
    if len(remaining) % 2 != 0:
        err = "%s tag requires 3, 5, 7... arguments " % tag_name
        err += "as you require 'field-name' and 'field-value'"
        raise template.TemplateSyntaxError(err)
    
    action_name = get_str(tag_name, action_name)
    try:
        url_text = (False, get_str(tag_name, url_text))
    except template.TemplateSyntaxError: #url_text was a variable
        url_text = (True, url_text)
    
    other_fields = []
    for field_name, field_value in zip(remaining[::2], remaining[1::2]):
        try:
            new_field_name = (False, get_str(tag_name, field_name))
        except template.TemplateSyntaxError:
            #It is a variable!
            new_field_name = (True, field_name)
            
        try:
            new_field_value = (False, get_str(tag_name, field_value))
        except template.TemplateSyntaxError:
            #It is a variable
            new_field_value = (True, field_value)
        
        other_fields.append((new_field_name, new_field_value))
    
    return ActionLinkNode2(tag_name, action_name, url_text, other_fields)
    

class ActionLinkNode2(template.Node):
    def __init__(self, tag_name, action_name, url_text, other_fields):
        self.tag_name = tag_name
        self.action_name = action_name
        if url_text[0]:
            self.url_text = (True, template.Variable(url_text[1]))
        else:
            self.url_text = (False, url_text[1])
        
        self.other_fields = []
        for field_name, field_value in other_fields:
            if field_name[0]:
                name = (True, template.Variable(field_name[1]))
            else:
                name = (False, field_name[1])
            
            if field_value[0]:
                value = (True, template.Variable(field_value[1]))
            else:
                value = (False, field_value[1])
            
            self.other_fields.append((name, value))
        
    
    def render(self, context):
        form_link = string.Template(
        """
        <div style="display:none">
            <form name="${form_name}" action="${form_action}" method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}" />
                <input type="hidden" name="action_name" value="${action_name}" />
                ${other_fields}
            </form>
        </div>
        <a href="javascript: document.${form_name}.submit();">${url_text}</a>
        """)
        
        if "action_link_count" not in context.render_context:
            context.render_context["action_link_count"] = 0
        context.render_context["action_link_count"] += 1
        
        form_name = "formlink_"+str(context.render_context["action_link_count"])
        form_action = reverse(game_action_resolver)
        
        #CSRF-TOKEN Taken from django.template.defaulttags.CsrfTokenNode
        csrf_token = context.get('csrf_token', None)
        if csrf_token:
            if csrf_token == 'NOTPROVIDED':
                return format_html("")
            else:
                csrf_token = format_html(csrf_token)
        else:
            # It's very probable that the token is missing because of
            # misconfiguration, so we raise a warning
            from django.conf import settings
            if settings.DEBUG:
                import warnings
                warnings.warn("CSRF_TOKEN required as action_link was used in a template,\
                but the context did not provide the value.  This is usually caused by not using RequestContext.")
            return u''
        #END CSRF TOKEN
        
        #Resolve url_text if it is a variable
        if self.url_text[0]:
            try:
                url_text_resolved = self.url_text[1].resolve(context)
            except VariableDoesNotExist:
                return u""
        else:
            url_text_resolved = self.url_text[1]
        
        other_fields_html = ""
        #Other fields may have variables in them
        row = string.Template(\
        """<input type="hidden" name="${field_name}" value="${field_value}" />
        """)
        
        for field_name, field_value in self.other_fields:
            if field_name[0]:
                try:
                    name = field_name[1].resolve(context)
                except VariableDoesNotExist:
                    return u""
            else:
                name = field_name[1]
            
            if field_value[0]:
                try:
                    value = field_value[1].resolve(context)
                except VariableDoesNotExist:
                    return u""
            else:
                value = field_value[1]
            
            other_fields_html += row.substitute(field_name=name,
                                                field_value=value)
        
        
        final_html = form_link.substitute(
            form_name=form_name,
            form_action=form_action,
            csrf=csrf_token,
            action_name=self.action_name,
            url_text=url_text_resolved,
            other_fields=other_fields_html
        )
        
        return mark_safe(final_html)


@register.filter
def mod(value, arg):
    """Return value modulo arg"""
    return int(value) % arg


@register.filter
def div( value, arg ):
    """Divides the value; argument is the divisor."""
    try:
        return float(value) / arg
    except:
        print("v", value)
        print("a", arg)
        return ""

@register.filter
def ceil(value):
    try:
        return int(maths.ceil(value))
    except:
        return ""
