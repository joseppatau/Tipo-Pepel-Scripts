# MenuTitle: Intermediate Axis Engine
# -*- coding: utf-8 -*-
# Description: Creates and manages intermediate layers using axis-based coordinates with continuous interpolation and preview support.
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# If you find this script useful, you can show your appreciation by purchasing any font at: https://www.myfonts.com/collections/tipo-pepel-foundry
# License: MIT
# Description: Preview and create intermediate glyphs with continuous weight blending
# Author: Designed by Josep Patau Bellart, programmed with AI tools
# License: MIT

from GlyphsApp import *
from vanilla import *
from AppKit import *
import objc
import math
import os
import tempfile
import webbrowser
import codecs
import json
import subprocess
from os import system, path
from AppKit import NSClassFromString, NSBundle, NSEvent, NSAlternateKeyMask, NSShiftKeyMask
import codecs
from GlyphsApp import Glyphs, Message
from Foundation import NSMutableDictionary, NSArray

# ---------------------------
# GLOBAL VARIABLE to prevent multiple instances
# ---------------------------
_panel_instance = None

# --- Constantes para el HTML (añadidas desde web type intermediate.py) ---
UNICODE_BULLET = "•"
FONT_TEST_NAMES = [
    ("English", "Amplect Lap"),
    ("Spanish", "Hombre Huevo"),
    ("German", "Schweiß Gequake"),
    ("French", "Voix Ambigue"),
    ("Italian", "Fece Aiuole"),
    ("Portuguese", "Açúcar Caça"),
]

# --- Funciones auxiliares para el HTML (añadidas desde web type intermediate.py) ---
def currentOTVarExportPath():
    """Obtiene la ruta de exportación de fuentes variables."""
    exportPath = Glyphs.defaults["GXExportPathManual"]
    if Glyphs.versionNumber and Glyphs.versionNumber >= 3:
        useExportPath = Glyphs.defaults["GXExportUseExportPath"]
    else:
        useExportPath = Glyphs.defaults["GXPluginUseExportPath"]
    if useExportPath:
        exportPath = Glyphs.defaults["GXExportPath"]
    return exportPath

def otVarFamilyName(thisFont):
    """Obtiene el nombre de familia de la fuente variable."""
    if thisFont.customParameters["Variable Font Family Name"]:
        return thisFont.customParameters["Variable Font Family Name"]
    else:
        return thisFont.familyName

def otVarFullName(thisFont):
    """Obtiene el nombre completo de la fuente variable."""
    familyName = otVarFamilyName(thisFont)
    styleName = thisFont.customParameters["variableStyleName"]
    if styleName:
        fullName = f"{familyName} {styleName}"
        fullName = fullName.replace("Italic Italic", "Italic")
        fullName = fullName.replace("Roman Roman", "Roman")
        return fullName
    else:
        return familyName

def otVarSuffix():
    """Determina la extensión del archivo según las preferencias de exportación."""
    suffix = "ttf"
    for webSuffix in ("woff", "woff2"):
        preference = Glyphs.defaults["GXExport%s" % webSuffix.upper()]
        if preference:
            suffix = webSuffix
    return suffix

def otVarFileName(thisFont, thisInstance=None):
    """Genera el nombre del archivo de fuente variable."""
    suffix = otVarSuffix()
    if thisInstance is not None:
        fileName = thisInstance.fileName()
        if fileName.endswith(".otf"):
            fileName = fileName[:-4]
        if not fileName:
            fileName = thisInstance.customParameters["fileName"]
            if not fileName:
                familyName = thisInstance.font.familyName
                fileName = f"{familyName}-{thisInstance.name}".replace(" ", "")
        return f"{fileName}.{suffix}"
    elif thisFont.customParameters["Variable Font File Name"] or thisFont.customParameters["variableFileName"]:
        fileName = thisFont.customParameters["Variable Font File Name"]
        if not fileName:
            fileName = thisFont.customParameters["variableFileName"]
        return f"{fileName}.{suffix}"
    else:
        familyName = otVarFamilyName(thisFont)
        if hasattr(Glyphs, 'versionString') and Glyphs.versionString >= "3.0.3":
            fileName = f"{familyName}VF.{suffix}"
        else:
            fileName = f"{familyName}GX.{suffix}"
        return fileName.replace(" ", "")

def generateAxisDict(thisFont):
    """Genera un diccionario con la información de los ejes variables."""
    axisDict = {}
    
    # Verificar si hay parámetros Axis Location
    fontHasAxisLocationParameters = True
    for thisMaster in thisFont.masters:
        if not thisMaster.customParameters["Axis Location"]:
            fontHasAxisLocationParameters = False
            break
    
    if fontHasAxisLocationParameters:
        # Con Axis Location parameters
        for m in thisFont.masters:
            for axisLocation in m.customParameters["Axis Location"]:
                axisName = axisLocation["Axis"]
                axisPos = float(axisLocation["Location"])
                if axisName not in axisDict:
                    axisDict[axisName] = {"min": axisPos, "max": axisPos}
                else:
                    if axisPos < axisDict[axisName]["min"]:
                        axisDict[axisName]["min"] = axisPos
                    if axisPos > axisDict[axisName]["max"]:
                        axisDict[axisName]["max"] = axisPos
    else:
        # Sin Axis Location parameters
        for i, axis in enumerate(thisFont.axes):
            try:
                # Glyphs 3
                axisName, axisTag = axis.name, axis.axisTag
            except:
                # Glyphs 2
                axisName, axisTag = axis["Name"], axis["Tag"]
            
            axisDict[axisName] = {
                "tag": axisTag,
                "min": 0,
                "max": 0
            }
            
            # Buscar valores mínimos y máximos en los masters
            for thisMaster in thisFont.masters:
                if i < len(thisMaster.axes):
                    value = thisMaster.axes[i]
                    if value < axisDict[axisName]["min"]:
                        axisDict[axisName]["min"] = value
                    if value > axisDict[axisName]["max"]:
                        axisDict[axisName]["max"] = value
    
    return axisDict

def allOTVarSliders(thisFont):
    """Genera los controles deslizantes HTML para cada eje variable."""
    axisDict = generateAxisDict(thisFont)
    html = ""
    
    for axis in thisFont.axes:
        try:
            # Glyphs 3
            axisName = axis.name
            axisTag = axis.axisTag
        except:
            # Glyphs 2
            axisName = axis["Name"]
            axisTag = axis["Tag"]
        
        if axisName in axisDict:
            minValue = axisDict[axisName]["min"]
            maxValue = axisDict[axisName]["max"]
            
            # Valor inicial (usar el primer master como referencia)
            startValue = minValue
            if thisFont.masters:
                firstMaster = thisFont.masters[0]
                axisIndex = [a.name for a in thisFont.axes].index(axisName) if hasattr(axis, 'name') else \
                           [a["Name"] for a in thisFont.axes].index(axisName)
                if axisIndex < len(firstMaster.axes):
                    startValue = firstMaster.axes[axisIndex]
            
            html += f'\t\t\t<div class="labeldiv"><label class="sliderlabel" id="label_{axisTag}" name="{axisName}">{axisName}</label><input type="range" min="{minValue}" max="{maxValue}" value="{startValue}" class="slider" id="{axisTag}" oninput="updateSlider();"></div>\n'
    
    return html

def getTestNameForLanguage(language_name):
    """Obtiene el par de palabras para un idioma específico."""
    for lang, test_name in FONT_TEST_NAMES:
        if lang.lower() == language_name.lower():
            return test_name
    return FONT_TEST_NAMES[0][1]  # Por defecto: English

def createSampleText():
    """Crea el texto de muestra con todas las combinaciones de idiomas."""
    sample_text = ""
    
    for i, (language_name, two_words) in enumerate(FONT_TEST_NAMES):
        # Separador entre idiomas (excepto el primero)
        if i > 0:
            sample_text += f"\n{UNICODE_BULLET * 3}\n"
        
        # Nombre del idioma
        sample_text += f"<span style='font-size: 0.7em; opacity: 0.7;'>{language_name}</span>\n"
        
        # Dos palabras centradas
        sample_text += f"<div style='text-align: center; font-size: 1.5em; margin: 0.5em 0;'>{two_words}</div>"
    
    return sample_text

def createHTMLTest(font_name, export_path):
    """Crea el archivo HTML de prueba para la fuente variable."""
    
    # Obtener la fuente actual
    thisFont = Glyphs.font
    
    # Generar controles deslizantes
    otVarSliders = allOTVarSliders(thisFont)
    
    # Configuración CSS inicial para variación
    variationCSS = ""
    if thisFont.axes:
        try:
            firstMaster = thisFont.masters[0]
            for i, axis in enumerate(thisFont.axes):
                axisTag = axis.axisTag
                value = firstMaster.axes[i] if i < len(firstMaster.axes) else 0
                if variationCSS:
                    variationCSS += ", "
                variationCSS += f'"{axisTag}" {value}'
        except:
            variationCSS = '"wght" 400'
    
    # Texto de muestra
    sampleText = createSampleText()
    
    # HTML template
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Variable Font Test: {font_name}</title>
    <style>
        @font-face {{
            font-family: "{font_name}";
            src: url("{font_name.replace(' ', '')}VF.woff2");
        }}
        
        body {{
            font-family: sans-serif;
            margin: 20px;
            padding: 0;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .font-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        
        .controls {{
            background: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        
        .labeldiv {{
            margin-bottom: 15px;
        }}
        
        .sliderlabel {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}
        
        .slider {{
            width: 100%;
            height: 25px;
            -webkit-appearance: none;
            background: #ddd;
            border-radius: 5px;
            outline: none;
        }}
        
        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 25px;
            height: 25px;
            background: #4CAF50;
            border-radius: 50%;
            cursor: pointer;
        }}
        
        .sample-container {{
            margin-top: 30px;
            padding: 30px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            min-height: 400px;
        }}
        
        .sample-text {{
            font-family: "{font_name}", sans-serif;
            font-size: 40px;
            line-height: 1.4;
            color: #333;
            font-variation-settings: {variationCSS};
        }}
        
        .language-separator {{
            text-align: center;
            color: #999;
            margin: 20px 0;
            font-size: 24px;
        }}
        
        .language-title {{
            font-size: 0.7em;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .two-words {{
            text-align: center;
            font-size: 1.5em;
            margin: 0.5em 0;
        }}
        
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        
        @media (prefers-color-scheme: dark) {{
            body {{
                background: #1a1a1a;
                color: #e0e0e0;
            }}
            
            .container {{
                background: #2d2d2d;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }}
            
            .controls, .font-info {{
                background: #3d3d3d;
            }}
            
            .sample-container {{
                background: #2d2d2d;
                border-color: #444;
            }}
            
            .sample-text {{
                color: #e0e0e0;
            }}
            
            h1, .sliderlabel {{
                color: #e0e0e0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Variable Font Test: {font_name}</h1>
        
        <div class="font-info">
            <strong>Font Family:</strong> {font_name}<br>
            <strong>Variable Axes:</strong> {len(thisFont.axes)}
        </div>
        
        <div class="controls">
            <h2>Variable Axes Controls</h2>
            {otVarSliders}
            
            <div class="labeldiv">
                <label class="sliderlabel" id="label_fontsize" name="Font Size">Font Size</label>
                <input type="range" min="10" max="200" value="40" class="slider" id="fontsize" oninput="updateSlider();">
            </div>
            
            <div class="labeldiv">
                <label class="sliderlabel" id="label_lineheight" name="Line Height">Line Height</label>
                <input type="range" min="50" max="200" value="120" class="slider" id="lineheight" oninput="updateSlider();">
            </div>
        </div>
        
        <div class="sample-container">
            <div class="sample-text" id="sampleText" contenteditable="true">
                {sampleText}
            </div>
        </div>
        
        <div class="footer">
            <p>Click on the text above to edit it. Use the sliders to adjust font variation settings.</p>
        </div>
    </div>
    
    <script>
        function updateSlider() {{
            const sampleText = document.getElementById('sampleText');
            const sliders = document.getElementsByClassName('slider');
            let settings = [];
            
            for (let slider of sliders) {{
                const label = document.getElementById('label_' + slider.id);
                if (label) {{
                    label.textContent = label.getAttribute('name') + ': ' + slider.value;
                    
                    if (slider.id === 'fontsize') {{
                        sampleText.style.fontSize = slider.value + 'px';
                        label.textContent += 'px';
                    }} else if (slider.id === 'lineheight') {{
                        sampleText.style.lineHeight = (slider.value / 100) + 'em';
                        label.textContent += '%';
                    }} else {{
                        settings.push('"' + slider.id + '" ' + slider.value);
                    }}
                }}
            }}
            
            if (settings.length > 0) {{
                sampleText.style.fontVariationSettings = settings.join(', ');
            }}
        }}
        
        function resetToDefault() {{
            const sliders = document.getElementsByClassName('slider');
            for (let slider of sliders) {{
                if (slider.id === 'fontsize') {{
                    slider.value = 40;
                }} else if (slider.id === 'lineheight') {{
                    slider.value = 120;
                }} else {{
                    // Reset to min value for variable axes
                    slider.value = parseFloat(slider.min);
                }}
            }}
            updateSlider();
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            updateSlider();
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {{
                if (e.ctrlKey) {{
                    if (e.key === 'r') {{
                        e.preventDefault();
                        resetToDefault();
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    # Guardar el archivo HTML
    html_filename = f"{font_name.replace(' ', '_')}_test.html"
    html_path = os.path.join(export_path, html_filename)
    
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML creado: {html_path}")
        return html_path
    except Exception as e:
        print(f"❌ Error al crear HTML: {e}")
        return None

# ---------------------------
# WEB PREVIEW FUNCTIONALITY (adapted from Variable Font Test HTML.py)
# ---------------------------
def createWebPreview(font, axisValues, text="Obvious Xylophone"):
    """Create an interactive HTML preview with sliders for all axes"""
    try:
        # Crear archivo HTML en carpeta de Descargas
        downloads_dir = os.path.expanduser("~/Downloads")
        if not os.path.exists(downloads_dir):
            downloads_dir = tempfile.gettempdir()
        
        html_file = os.path.join(downloads_dir, "glyphs_interactive_preview.html")
        
        # Get font information
        font_name = font.familyName if hasattr(font, 'familyName') else "Current Font"
        
        # Get axes information
        axes_info = []
        if hasattr(font, 'axes'):
            for idx, axis in enumerate(font.axes):
                try:
                    axis_name = getattr(axis, "name", f"Axis {idx+1}")
                    axis_tag = getattr(axis, "axisTag", f"axis{idx}")
                    
                    # Get min, max, and default values from masters
                    master_values = [m.axes[idx] for m in font.masters]
                    min_val = min(master_values)
                    max_val = max(master_values)
                    
                    # Get current value from axisValues
                    current_val = None
                    for key, val in axisValues.items():
                        key_lower = key.lower()
                        axis_name_lower = axis_name.lower() if axis_name else ""
                        axis_tag_lower = axis_tag.lower() if axis_tag else ""
                        
                        if (key_lower == axis_name_lower or 
                            (axis_tag_lower and key_lower == axis_tag_lower)):
                            try:
                                current_val = float(val)
                                break
                            except:
                                continue
                    
                    if current_val is None:
                        current_val = master_values[0] if master_values else min_val
                    
                    # Ensure value is within range
                    current_val = max(min_val, min(current_val, max_val))
                    
                    axes_info.append({
                        'name': axis_name,
                        'tag': axis_tag,
                        'min': min_val,
                        'max': max_val,
                        'default': current_val,
                        'current': current_val
                    })
                    
                except Exception as e:
                    print(f"Error processing axis {idx}: {e}")
        
        # Create HTML content
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Interactive Font Preview: ###FONT_NAME###</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }
        
        h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }
        
        .subtitle {
            font-size: 18px;
            opacity: 0.9;
            font-weight: 400;
        }
        
        .preview-section {
            padding: 40px;
        }
        
        .preview-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 40px;
            border: 2px solid #e9ecef;
            text-align: center;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .preview-text {
            font-size: 280px;
            line-height: 1;
            font-weight: 700;
            color: #212529;
            font-feature-settings: "kern" on, "liga" on, "calt" on;
            font-variation-settings: ###VARIATION_SETTINGS###;
            transition: all 0.3s ease;
            max-width: 100%;
            word-wrap: break-word;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .controls-section {
            padding: 0 40px 40px;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .axis-control {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        
        .axis-control:hover {
            border-color: #4facfe;
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .axis-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .axis-name {
            font-size: 20px;
            font-weight: 600;
            color: #495057;
        }
        
        .axis-value {
            font-size: 24px;
            font-weight: 700;
            color: #4facfe;
            background: white;
            padding: 5px 15px;
            border-radius: 10px;
            border: 2px solid #dee2e6;
            min-width: 80px;
            text-align: center;
        }
        
        .slider-container {
            margin: 15px 0;
        }
        
        .slider-labels {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
            color: #6c757d;
        }
        
        input[type="range"] {
            width: 100%;
            height: 12px;
            -webkit-appearance: none;
            appearance: none;
            background: linear-gradient(to right, #dee2e6, #4facfe);
            border-radius: 10px;
            outline: none;
            cursor: pointer;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: white;
            border: 3px solid #4facfe;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }
        
        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        input[type="number"] {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        input[type="number"]:focus {
            outline: none;
            border-color: #4facfe;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.2);
        }
        
        button {
            padding: 12px 25px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .text-controls {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            margin-top: 30px;
        }
        
        .text-input-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        #textInput {
            flex: 1;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            font-size: 18px;
            transition: all 0.3s ease;
        }
        
        #textInput:focus {
            outline: none;
            border-color: #4facfe;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.2);
        }
        
        .font-size-control {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 20px;
        }
        
        .font-size-control label {
            font-weight: 600;
            color: #495057;
            min-width: 100px;
        }
        
        #fontSizeSlider {
            flex: 1;
        }
        
        #fontSizeValue {
            width: 80px;
            text-align: center;
        }
        
        .status-bar {
            background: #f8f9fa;
            padding: 15px 40px;
            border-top: 2px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #6c757d;
        }
        
        .copy-button {
            background: #28a745;
            padding: 8px 15px;
            border-radius: 8px;
            color: white;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .copy-button:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 24px; }
            .subtitle { font-size: 16px; }
            .preview-text { font-size: 120px; }
            .preview-section { padding: 20px; }
            .controls-section { padding: 0 20px 20px; }
            .controls-grid { grid-template-columns: 1fr; }
            .axis-name { font-size: 18px; }
            .axis-value { font-size: 20px; }
            .input-group { flex-direction: column; }
            .text-input-group { flex-direction: column; }
        }
        
        @media (prefers-color-scheme: dark) {
            body { background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); }
            .container { background: #2d3748; color: #e2e8f0; }
            header { background: linear-gradient(135deg, #2b6cb0 0%, #4299e1 100%); }
            .preview-container { background: #4a5568; border-color: #718096; }
            .preview-text { color: #e2e8f0; }
            .axis-control { background: #4a5568; border-color: #718096; }
            .axis-name { color: #e2e8f0; }
            .axis-value { background: #2d3748; color: #63b3ed; border-color: #4a5568; }
            input[type="range"] { background: linear-gradient(to right, #718096, #63b3ed); }
            input[type="range"]::-webkit-slider-thumb { background: #2d3748; border-color: #63b3ed; }
            input[type="number"] { background: #2d3748; color: #e2e8f0; border-color: #4a5568; }
            button { background: linear-gradient(135deg, #2b6cb0 0%, #4299e1 100%); }
            .text-controls { background: #4a5568; border-color: #718096; }
            #textInput { background: #2d3748; color: #e2e8f0; border-color: #4a5568; }
            .status-bar { background: #4a5568; border-color: #718096; color: #a0aec0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Interactive Font Preview</h1>
            <div class="subtitle">###FONT_NAME### - Adjust sliders to see real-time changes</div>
        </header>
        
        <section class="preview-section">
            <div class="preview-container">
                <div id="previewText" class="preview-text">###TEXT###</div>
            </div>
        </section>
        
        <section class="controls-section">
            <div class="controls-grid" id="axisControls">
                ###AXIS_CONTROLS###
            </div>
            
            <div class="text-controls">
                <h3>Text Controls</h3>
                <div class="text-input-group">
                    <input type="text" id="textInput" value="###TEXT###" placeholder="Enter custom text...">
                    <button onclick="updateText()">Update Text</button>
                </div>
                
                <div class="font-size-control">
                    <label>Font Size:</label>
                    <input type="range" id="fontSizeSlider" min="50" max="500" value="280" oninput="updateFontSize()">
                    <input type="number" id="fontSizeValue" value="280" min="50" max="500" onchange="updateFontSizeFromInput()">
                </div>
            </div>
        </section>
        
        <div class="status-bar">
            <div>CSS Code: <code id="cssCode">font-variation-settings: ###VARIATION_SETTINGS###;</code></div>
            <a href="#" onclick="copyCSS()" class="copy-button">Copy CSS</a>
        </div>
    </div>

    <script>
        // Initialize axis values
        let axisValues = ###AXIS_VALUES_JSON###;
        
        // Update CSS and preview
        function updatePreview() {
            const previewText = document.getElementById('previewText');
            const cssCode = document.getElementById('cssCode');
            
            // Build variation settings string
            let variationSettings = [];
            for (const axis in axisValues) {
                variationSettings.push(`"${axis}" ${axisValues[axis]}`);
            }
            
            // Apply to preview
            previewText.style.fontVariationSettings = variationSettings.join(', ');
            
            // Update CSS code display
            cssCode.textContent = `font-variation-settings: ${variationSettings.join(', ')};`;
        }
        
        // Update specific axis value
        function updateAxis(axisTag, value) {
            axisValues[axisTag] = parseFloat(value);
            
            // Update the corresponding value display
            const valueDisplay = document.getElementById(`value_${axisTag}`);
            if (valueDisplay) {
                valueDisplay.textContent = Math.round(value * 10) / 10;
            }
            
            // Update the input field
            const inputField = document.getElementById(`input_${axisTag}`);
            if (inputField) {
                inputField.value = value;
            }
            
            updatePreview();
        }
        
        // Update text content
        function updateText() {
            const textInput = document.getElementById('textInput');
            const previewText = document.getElementById('previewText');
            previewText.textContent = textInput.value || 'Preview Text';
        }
        
        // Update font size from slider
        function updateFontSize() {
            const slider = document.getElementById('fontSizeSlider');
            const input = document.getElementById('fontSizeValue');
            const previewText = document.getElementById('previewText');
            
            const size = slider.value;
            input.value = size;
            previewText.style.fontSize = `${size}px`;
        }
        
        // Update font size from input
        function updateFontSizeFromInput() {
            const input = document.getElementById('fontSizeValue');
            const slider = document.getElementById('fontSizeSlider');
            const previewText = document.getElementById('previewText');
            
            let size = parseInt(input.value);
            if (size < 50) size = 50;
            if (size > 500) size = 500;
            
            input.value = size;
            slider.value = size;
            previewText.style.fontSize = `${size}px`;
        }
        
        // Copy CSS code to clipboard
        function copyCSS() {
            const cssCode = document.getElementById('cssCode').textContent;
            navigator.clipboard.writeText(cssCode).then(() => {
                alert('CSS copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        }
        
        // Reset all axes to default values
        function resetAxes() {
            ###RESET_SCRIPT###
            updatePreview();
        }
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            updatePreview();
            
            // Add reset button dynamically
            const axisControls = document.getElementById('axisControls');
            const resetDiv = document.createElement('div');
            resetDiv.className = 'axis-control';
            resetDiv.innerHTML = `
                <div class="axis-header">
                    <div class="axis-name">Reset All</div>
                    <div class="axis-value">↺</div>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="resetAxes()" style="width: 100%; padding: 15px; font-size: 18px;">
                        Reset to Default Values
                    </button>
                </div>
            `;
            axisControls.appendChild(resetDiv);
        });
    </script>
</body>
</html>"""
        
        # Build axis controls HTML
        axis_controls_html = ""
        for axis in axes_info:
            axis_controls_html += f'''
                <div class="axis-control">
                    <div class="axis-header">
                        <div class="axis-name">{axis['name']} ({axis['tag']})</div>
                        <div class="axis-value" id="value_{axis['tag']}">{axis['current']}</div>
                    </div>
                    <div class="slider-container">
                        <div class="slider-labels">
                            <span>{axis['min']}</span>
                            <span>{axis['max']}</span>
                        </div>
                        <input type="range" id="slider_{axis['tag']}" 
                               min="{axis['min']}" max="{axis['max']}" 
                               value="{axis['current']}" step="1"
                               oninput="updateAxis('{axis['tag']}', this.value)">
                    </div>
                    <div class="input-group">
                        <input type="number" id="input_{axis['tag']}" 
                               value="{axis['current']}" 
                               min="{axis['min']}" max="{axis['max']}" step="1"
                               onchange="updateAxis('{axis['tag']}', this.value)">
                        <button onclick="document.getElementById('input_{axis['tag']}').value='{axis['default']}'; updateAxis('{axis['tag']}', '{axis['default']}')">
                            Reset
                        </button>
                    </div>
                </div>
            '''
        
        # Build variation settings string
        variation_settings = []
        for axis in axes_info:
            variation_settings.append(f'"{axis["tag"]}" {axis["current"]}')
        
        # Build axis values JSON
        axis_values_json = {}
        for axis in axes_info:
            axis_values_json[axis['tag']] = axis['current']
        
        # Build reset script
        reset_script_lines = []
        for axis in axes_info:
            reset_script_lines.append(f'axisValues["{axis["tag"]}"] = {axis["default"]};')
            reset_script_lines.append(f'document.getElementById("slider_{axis["tag"]}").value = {axis["default"]};')
            reset_script_lines.append(f'document.getElementById("input_{axis["tag"]}").value = {axis["default"]};')
            reset_script_lines.append(f'document.getElementById("value_{axis["tag"]}").textContent = {axis["default"]};')
        reset_script = "\n            ".join(reset_script_lines)
        
        # Replace placeholders
        replacements = (
            ("###FONT_NAME###", font_name),
            ("###TEXT###", text),
            ("###VARIATION_SETTINGS###", ", ".join(variation_settings) if variation_settings else '"wght" 400'),
            ("###AXIS_CONTROLS###", axis_controls_html if axis_controls_html else "<p>No axes defined</p>"),
            ("###AXIS_VALUES_JSON###", json.dumps(axis_values_json)),
            ("###RESET_SCRIPT###", reset_script)
        )
        
        for search, replace in replacements:
            html_content = html_content.replace(search, replace)
        
        # Write HTML file
        with codecs.open(html_file, "w", "utf-8-sig") as f:
            f.write(html_content)
        
        print(f"✅ Interactive web preview created: {html_file}")
        print(f"   Font: {font_name}")
        print(f"   Axes: {len(axes_info)}")
        
        return html_file
        
    except Exception as e:
        print(f"❌ Error creating web preview: {e}")
        import traceback
        traceback.print_exc()
        return None

# ---------------------------
# DEBUG HELPER
# ---------------------------
def debug_layer_info(glyph):
    """Print detailed information about all layers in a glyph"""
    if not glyph:
        return
    
    print(f"\n{'='*80}")
    print(f"DEBUG LAYER INFO FOR GLYPH: {glyph.name}")
    print(f"{'='*80}")
    
    font = Glyphs.font
    for idx, layer in enumerate(glyph.layers):
        print(f"\n--- Layer {idx}: '{layer.name if hasattr(layer, 'name') else 'No name'}' ---")
        
        # Basic info
        print(f"  Type: {type(layer)}")
        
        # Check if it's a master layer
        if hasattr(layer, 'associatedMasterId') and layer.associatedMasterId:
            master_id = layer.associatedMasterId
            master_name = "Unknown"
            for m in font.masters:
                if m.id == master_id:
                    master_name = m.name
                    break
            print(f"  Associated Master: {master_name} (ID: {master_id})")
        else:
            print(f"  Not associated with a master")
        
        # Check for brace notation in name
        if hasattr(layer, 'name') and layer.name:
            name = layer.name
            print(f"  Layer name: '{name}'")
            
            # Parse brace notation
            if name.startswith("{") and "}" in name:
                print(f"  ⚠️  BRACE NOTATION DETECTED IN NAME")
                try:
                    content = name[name.find("{")+1:name.find("}")]
                    parts = content.split(",")
                    print(f"  Parsed values: {parts}")
                except Exception as e:
                    print(f"  Error parsing brace: {e}")
        
        # Check attributes
        if hasattr(layer, 'attributes'):
            attrs = layer.attributes
            print(f"  Attributes type: {type(attrs)}")
            
            if isinstance(attrs, dict):
                print(f"  Attributes dict keys: {list(attrs.keys())}")
                
                # Check for special layer markers
                if attrs.get('isSpecialLayer'):
                    print(f"  ✅ isSpecialLayer: True")
                
                # Check for coordinates
                coords = attrs.get('coordinates')
                if coords:
                    print(f"  ✅ coordinates: {coords}")
                    print(f"  coordinates type: {type(coords)}")
                
                # Check for interpolation dict
                interp = attrs.get('interpolation')
                if interp:
                    print(f"  ✅ interpolation: {interp}")
                    if hasattr(interp, 'get'):
                        print(f"    - master: {interp.get('master')}")
                        print(f"    - coordinates: {interp.get('coordinates')}")
            
            elif attrs:
                print(f"  Attributes (not dict): {attrs}")
        else:
            print(f"  No attributes found")
        
        # Check for other properties
        if hasattr(layer, 'paths'):
            print(f"  Number of paths: {len(layer.paths) if layer.paths else 0}")
        
        if hasattr(layer, 'width'):
            print(f"  Width: {layer.width}")
    
    print(f"\n{'='*80}")

# ---------------------------
# HELPERS from visualizador intermediate.py
# ---------------------------
def parse_brace_from_name(lyr):
    """
    If layer.name is like {124,1,0} or {153,1,0,}, return a list of floats [124,1,0].
    Otherwise return None.
    """
    try:
        nm = lyr.name or ""
        nm = nm.strip()
        if nm.startswith("{") and nm.endswith("}"):
            inside = nm[1:-1].strip()
            if not inside:
                return None
            parts = [p.strip() for p in inside.split(",") if p.strip() != ""]
            vals = []
            for p in parts:
                try:
                    vals.append(float(p))
                except:
                    return None
            return vals
    except Exception:
        pass
    return None

def gather_weight_sources(font, glyph):
    """Gather all weight sources (masters + brace layers)"""
    sources = []

    # ---- MASTERS ----
    for m in font.masters:
        try:
            # assume axis 0 is Weight
            w = float(m.axes[0])
        except Exception:
            # fallback: search for axis named 'Weight'
            try:
                idx = next(i for i,a in enumerate(font.axes) if (a.name or "").lower() == "weight" or (getattr(a,"axisTag",None) or "").lower() == "wght")
                w = float(m.axes[idx])
            except Exception:
                w = 0.0

        # try to obtain the layer associated to this master
        layer = None
        try:
            layer = glyph.layerForKey_(m.id)
        except Exception:
            layer = None

        if not layer:
            for lyr in glyph.layers:
                try:
                    if getattr(lyr, "associatedMasterId", None) == m.id:
                        layer = lyr
                        break
                except Exception:
                    pass

        if not layer:
            try:
                layer = glyph.layers[0]
            except Exception:
                layer = None  # <-- ESTA LÍNEA FALTABA LA INDENTACIÓN

        sources.append((w, layer, f"master-{m.name or m.id}"))

    # ---- BRACE LAYERS ----
    for lyr in glyph.layers:
        vals = parse_brace_from_name(lyr)
        if vals and len(vals) >= 1:
            try:
                w = float(vals[0])
            except Exception:
                continue
            sources.append((w, lyr, lyr.name))

    # dedupe by (name, weight) keeping last occurrence, then sort by weight
    uniq = {}
    for w, lyr, nm in sources:
        uniq[(nm, float(w))] = (float(w), lyr, nm)
    out = [uniq[k] for k in uniq]
    out_sorted = sorted(out, key=lambda t: t[0])
    return out_sorted

def interpolate_layers_nodewise(layerA, layerB, t):
    """Interpolate between two layers by node coordinates"""
    try:
        newLayer = layerA.copy()
        
        pathsA = getattr(newLayer, "paths", None)
        pathsB = getattr(layerB, "paths", None)
        if pathsA is None or pathsB is None:
            return None
        if len(pathsA) != len(pathsB):
            return None

        # iterate paths and nodes
        for pi in range(len(pathsA)):
            pa = pathsA[pi]
            pb = pathsB[pi]
            nodesA = getattr(pa, "nodes", None)
            nodesB = getattr(pb, "nodes", None)
            if nodesA is None or nodesB is None:
                return None
            if len(nodesA) != len(nodesB):
                return None
            
            # interpolate node positions
            for ni in range(len(nodesA)):
                na = nodesA[ni]
                nb = nodesB[ni]
                try:
                    ax = float(na.x)
                    ay = float(na.y)
                    bx = float(nb.x)
                    by = float(nb.y)
                    ix = ax + (bx - ax) * t
                    iy = ay + (by - ay) * t
                    na.x = ix
                    na.y = iy
                except Exception:
                    return None

        # interpolate width
        try:
            wa = float(getattr(layerA, "width", 0))
            wb = float(getattr(layerB, "width", 0))
            newLayer.width = wa + (wb - wa) * t
        except Exception:
            pass

        return newLayer
    except Exception as e:
        print(f"interpolate_nodes error: {e}")
        return None

def find_glyph(font, ch):
    if not font or not ch:
        return None
    if ch in font.glyphs:
        return font.glyphs[ch]
    for g in font.glyphs:
        if g.unicode:
            try:
                if chr(int(g.unicode, 16)) == ch:
                    return g
            except Exception:
                pass
    return None

# ---------------------------
# SIMPLIFIED PREVIEW VIEW
# ---------------------------
class EnhancedPreviewView(NSView):
    def initWithFrame_(self, frame):
        self = objc.super(EnhancedPreviewView, self).initWithFrame_(frame)
        if self is None:
            return None
        
        # Basic properties
        self.character = "H"
        self.metrics = None
        self.showXbeam = True
        self.showYbeam = True
        self.xbeamPosition = 520
        self.ybeamPosition = 300
        self.axisValues = {}
        
        # Cache
        self.cachedPath = None
        self.cachedLayer = None
        
        return self

    @objc.python_method
    def setCharacter_(self, ch):
        if ch and len(ch) > 0:
            self.character = ch
        else:
            self.character = " "
        self.cachedPath = None
        self.cachedLayer = None
        self.setNeedsDisplay_(True)

    @objc.python_method
    def setMetrics_(self, metrics):
        self.metrics = metrics
        if metrics and 'xh' in metrics:
            real_xheight = float(metrics['xh'])
            self.xbeamPosition = real_xheight
        self.cachedPath = None
        self.cachedLayer = None
        self.setNeedsDisplay_(True)
        
    @objc.python_method
    def setXbeamPosition_(self, position):
        if self.metrics:
            desc = float(self.metrics.get('desc', 0))
            asc = float(self.metrics.get('asc', 1000))
            self.xbeamPosition = max(desc, min(position, asc))
        else:
            self.xbeamPosition = position
        self.setNeedsDisplay_(True)
        
    @objc.python_method
    def setYbeamPosition_(self, position):
        if self.metrics:
            layer = self.getCurrentLayer()
            if layer:
                max_width = float(layer.width)
                self.ybeamPosition = max(0, min(position, max_width))
            else:
                self.ybeamPosition = max(0, min(position, 1000))
        else:
            self.ybeamPosition = position
        self.setNeedsDisplay_(True)
        
    @objc.python_method
    def setShowXbeam_(self, show):
        self.showXbeam = bool(show)
        self.setNeedsDisplay_(True)
        
    @objc.python_method
    def setShowYbeam_(self, show):
        self.showYbeam = bool(show)
        self.setNeedsDisplay_(True)
        
    @objc.python_method
    def setAxisValues_(self, axisValues):
        self.axisValues = axisValues or {}
        self.cachedPath = None
        self.cachedLayer = None
        self.setNeedsDisplay_(True)

    @objc.python_method
    def getCurrentMaster(self):
        """Get current master based on metrics"""
        if not self.metrics:
            return None
        try:
            font = Glyphs.font
            if not font or not font.masters:
                return None
                
            masterID = self.metrics.get('masterID')
            masterIndex = self.metrics.get('masterIndex', 0)
            
            # Search by ID first
            if masterID:
                for master in font.masters:
                    if master.id == masterID:
                        return master
            
            # Fallback to index
            if 0 <= masterIndex < len(font.masters):
                return font.masters[masterIndex]
            
            # Last resort: first master
            return font.masters[0]
            
        except Exception as e:
            print(f"❌ ERROR in getCurrentMaster: {e}")
            return None

    @objc.python_method
    def getCurrentLayer(self):
        """Get interpolated layer using continuous multi-axis blending"""
        try:
            font = Glyphs.font
            if not font:
                print("[DEBUG] No font available")
                return None
                
            glyph = find_glyph(font, self.character)
            if not glyph:
                print(f"[DEBUG] No glyph found for: '{self.character}'")
                return None
            
            # If no axis values, return master layer
            if not self.axisValues:
                print("[DEBUG] No axis values, returning master layer")
                return self.getMasterLayer(glyph)
            
            print(f"\n{'='*60}")
            print(f"[DEBUG] getCurrentLayer called for glyph: {glyph.name}")
            print(f"[DEBUG] Character: '{self.character}'")
            print(f"[DEBUG] Current axis values: {self.axisValues}")
            
            # ---- STEP 1: Collect all layers with coordinates ----
            layers_with_coords = []
            
            # Add master layers
            for m in font.masters:
                layer = None
                try:
                    layer = glyph.layerForKey_(m.id)
                except Exception:
                    layer = None

                if not layer:
                    for lyr in glyph.layers:
                        try:
                            if getattr(lyr, "associatedMasterId", None) == m.id:
                                layer = lyr
                                break
                        except Exception:
                            pass

                if layer:
                    # Get master's axis values
                    coords = []
                    for axis in font.axes:
                        idx = list(font.axes).index(axis)
                        coords.append(float(m.axes[idx]))
                    layers_with_coords.append((coords, layer, f"master-{m.name}"))
            
            # Add brace layers
            brace_layers_found = 0
            for lyr in glyph.layers:
                # Method 1: Parse from name format {value1,value2,...}
                vals = parse_brace_from_name(lyr)
                if vals:
                    try:
                        # Ensure we have enough values for all axes
                        if len(vals) >= len(font.axes):
                            coords = [float(v) for v in vals[:len(font.axes)]]
                            layers_with_coords.append((coords, lyr, lyr.name))
                            brace_layers_found += 1
                        else:
                            # Pad with zeros if needed
                            coords = [float(v) for v in vals]
                            while len(coords) < len(font.axes):
                                coords.append(0.0)
                            layers_with_coords.append((coords, lyr, lyr.name))
                            brace_layers_found += 1
                    except Exception:
                        continue
                
                # Method 2: Check for coordinates in attributes
                elif hasattr(lyr, 'attributes'):
                    attrs = lyr.attributes
                    if isinstance(attrs, dict):
                        # Check for coordinates attribute
                        coords_attr = attrs.get('coordinates')
                        if coords_attr:
                            try:
                                coords = [float(c) for c in coords_attr]
                                layers_with_coords.append((coords, lyr, lyr.name))
                                brace_layers_found += 1
                            except Exception:
                                pass
            
            print(f"[DEBUG] Total layers found: {len(layers_with_coords)} (masters: {len(font.masters)}, brace: {brace_layers_found})")
            
            # ---- STEP 2: Convert target axis values to coordinate list ----
            target_coords = []
            for axis in font.axes:
                axis_name = axis.name
                axis_tag = getattr(axis, "axisTag", "")
                
                # Try to find matching value
                value = None
                for key, val in self.axisValues.items():
                    key_lower = key.lower()
                    axis_name_lower = axis_name.lower() if axis_name else ""
                    axis_tag_lower = axis_tag.lower() if axis_tag else ""
                    
                    if (key_lower == axis_name_lower or 
                        (axis_tag_lower and key_lower == axis_tag_lower)):
                        try:
                            value = float(val)
                            break
                        except Exception:
                            continue
                
                if value is None:
                    # Use master value as fallback
                    master = self.getCurrentMaster()
                    if master:
                        idx = list(font.axes).index(axis)
                        value = float(master.axes[idx])
                    else:
                        value = 0.0
                
                target_coords.append(value)
            
            print(f"[DEBUG] Target coordinates: {target_coords}")
            
            # ---- STEP 3: Check for exact match first ----
            exact_match = None
            for coords, layer, name in layers_with_coords:
                if len(coords) == len(target_coords):
                    is_exact = True
                    for i in range(len(coords)):
                        if abs(coords[i] - target_coords[i]) > 0.1:
                            is_exact = False
                            break
                    if is_exact:
                        exact_match = layer
                        print(f"[DEBUG] Exact match found: {name} with coords {coords}")
                        return layer
            
            # ---- STEP 4: If we have brace layers, try interpolation between them first ----
            if brace_layers_found > 0:
                print(f"[DEBUG] Found {brace_layers_found} brace layers, attempting brace-based interpolation...")
                
                # Find the two closest brace layers
                brace_layers = []
                for coords, layer, name in layers_with_coords:
                    # Only consider brace layers (not masters)
                    if name.startswith("{") or (hasattr(layer, 'attributes') and layer.attributes.get('isSpecialLayer')):
                        brace_layers.append((coords, layer, name))
                
                if len(brace_layers) >= 2:
                    # Calculate distances
                    brace_with_distances = []
                    for coords, layer, name in brace_layers:
                        distance = 0
                        for i in range(len(coords)):
                            diff = coords[i] - target_coords[i]
                            distance += diff * diff
                        distance = math.sqrt(distance)
                        brace_with_distances.append((distance, coords, layer, name))
                    
                    brace_with_distances.sort(key=lambda x: x[0])
                    
                    # Check if we should use brace layers instead of masters
                    dist1, coords1, layer1, name1 = brace_with_distances[0]
                    dist2, coords2, layer2, name2 = brace_with_distances[1]
                    
                    print(f"[DEBUG] Two closest brace layers:")
                    print(f"[DEBUG]   1. '{name1}' distance: {dist1:.2f}, coords: {coords1}")
                    print(f"[DEBUG]   2. '{name2}' distance: {dist2:.2f}, coords: {coords2}")
                    
                    # Only use brace interpolation if we're closer to brace layers than to any master
                    # or if we're between brace layers
                    
                    # Check if target is between these two brace layers
                    is_between = True
                    for i in range(len(target_coords)):
                        if not (min(coords1[i], coords2[i]) <= target_coords[i] <= max(coords1[i], coords2[i])):
                            is_between = False
                            break
                    
                    if is_between:
                        print(f"[DEBUG] Target is between brace layers, attempting interpolation...")
                        
                        # Calculate interpolation factor for each axis independently
                        # For multi-axis, we need a more sophisticated approach
                        # Let's use the weight axis (first axis) as primary
                        if abs(coords2[0] - coords1[0]) > 0.001:
                            t_weight = (target_coords[0] - coords1[0]) / (coords2[0] - coords1[0])
                        else:
                            t_weight = 0.5
                        
                        print(f"[DEBUG] Interpolation factor (based on weight): t={t_weight:.3f}")
                        
                        # Try nodewise interpolation
                        interp = interpolate_layers_nodewise(layer1, layer2, t_weight)
                        if interp:
                            print(f"[DEBUG] Brace layer interpolation SUCCESSFUL")
                            return interp
                        else:
                            print(f"[DEBUG] Brace layer interpolation failed")
                    else:
                        print(f"[DEBUG] Target is not between these brace layers")
            
            # ---- STEP 5: Find closest master or brace layer (simple fallback) ----
            closest_distance = float('inf')
            closest_layer = None
            closest_name = None
            
            for coords, layer, name in layers_with_coords:
                distance = 0
                for i in range(len(coords)):
                    diff = coords[i] - target_coords[i]
                    distance += diff * diff
                distance = math.sqrt(distance)
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_layer = layer
                    closest_name = name
            
            print(f"[DEBUG] Closest layer overall: '{closest_name}' distance: {closest_distance:.2f}")
            
            # If very close, use it directly
            if closest_distance < 1.0:
                print(f"[DEBUG] Using closest layer (very close)")
                return closest_layer
            
            # ---- STEP 6: Try GSInstance interpolation (for complex multi-axis) ----
            print(f"[DEBUG] Attempting GSInstance interpolation...")
            try:
                inst = GSInstance.alloc().init()
                inst.font = font
                inst.axes = target_coords
                
                vf = inst.interpolatedFont
                if vf and glyph.name in vf.glyphs:
                    layer = vf.glyphs[glyph.name].layers[0]
                    print("[DEBUG] GSInstance interpolation SUCCESSFUL")
                    return layer
            except Exception as e:
                print(f"[DEBUG] GSInstance error: {e}")
            
            # ---- STEP 7: Final fallback ----
            print(f"[DEBUG] Using closest layer as final fallback: '{closest_name}'")
            return closest_layer or self.getMasterLayer(glyph)
            
        except Exception as e:
            print(f"❌ ERROR in getCurrentLayer: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    @objc.python_method
    def debugCurrentGlyph(self):
        """Debug function to print current glyph information"""
        try:
            font = Glyphs.font
            if not font:
                return
            
            glyph = find_glyph(font, self.character)
            if glyph:
                debug_layer_info(glyph)
        except Exception as e:
            print(f"❌ ERROR in debugCurrentGlyph: {e}")
            
    @objc.python_method
    def getMasterLayer(self, glyph):
        """Get current master layer"""
        try:
            master = self.getCurrentMaster()
            if not master:
                return glyph.layers[0] if glyph.layers else None

            # Find layer associated with master
            for layer in glyph.layers:
                if (hasattr(layer, 'associatedMasterId') and layer.associatedMasterId == master.id) or \
                   (hasattr(layer, 'masterId') and layer.masterId == master.id):
                    return layer

            # Fallback to first layer
            return glyph.layers[0] if glyph.layers else None
            
        except Exception as e:
            print(f"❌ ERROR in getMasterLayer: {e}")
            return glyph.layers[0] if glyph.layers else None

    @objc.python_method
    def getInterpolatedLayerViaInstance(self, glyph):
        """Fallback interpolation using GSInstance - improved version"""
        try:
            font = Glyphs.font
            inst = GSInstance.alloc().init()
            inst.font = font
            
            # Convert axis values to list in correct order
            axis_values = []
            for axis in font.axes:
                axis_name = axis.name
                axis_tag = getattr(axis, "axisTag", "")
                
                # Try to find matching value
                value = None
                for key, val in self.axisValues.items():
                    # Match by name or tag (case-insensitive)
                    key_lower = key.lower()
                    if (key_lower == axis_name.lower() or 
                        (axis_tag and key_lower == axis_tag.lower()) or
                        (axis_tag and key_lower == axis_tag.lower())):
                        try:
                            value = float(val)
                            print(f"[GSInstance] Found axis {axis_name}: {value}")
                            break
                        except Exception:
                            continue
                
                if value is None:
                    # Try to find by axis index (Weight is usually first)
                    axis_index = list(font.axes).index(axis)
                    axis_key = None
                    
                    # Common axis names
                    common_names = ['weight', 'wght', 'width', 'wdth', 'opsz', 'optical', 'ital', 'slnt']
                    for common in common_names:
                        if common in self.axisValues:
                            axis_key = common
                            break
                    
                    if axis_key and axis_index == 0:  # First axis is usually Weight
                        try:
                            value = float(self.axisValues[axis_key])
                            print(f"[GSInstance] Using {axis_key} for first axis: {value}")
                        except Exception:
                            value = 0.0
                    else:
                        # Use master value as fallback
                        master = self.getCurrentMaster()
                        if master:
                            value = float(master.axes[axis_index])
                            print(f"[GSInstance] Using master value for {axis_name}: {value}")
                        else:
                            value = 0.0
                
                axis_values.append(value)
            
            print(f"[GSInstance] Final axis values: {axis_values}")
            inst.axes = axis_values
            vf = inst.interpolatedFont
            
            if vf and glyph.name in vf.glyphs:
                print("[GSInstance] Interpolation successful")
                return vf.glyphs[glyph.name].layers[0]
            
            print("[GSInstance] Interpolation failed, using master layer")
            return self.getMasterLayer(glyph)
            
        except Exception as e:
            print(f"❌ ERROR in getInterpolatedLayerViaInstance: {e}")
            import traceback
            traceback.print_exc()
            return self.getMasterLayer(glyph)

    @objc.python_method
    def buildPathFromLayer(self, layer):
        if not layer:
            return None
        if self.cachedPath and self.cachedLayer == layer:
            return self.cachedPath
        
        try:
            if hasattr(layer, 'bezierPath'):
                bezier_path = layer.bezierPath
                if bezier_path and bezier_path.elementCount() > 0:
                    self.cachedPath = bezier_path
                    self.cachedLayer = layer
                    return bezier_path
            
            # Manual path construction
            path = NSBezierPath.bezierPath()
            if hasattr(layer, 'paths') and layer.paths:
                for glyph_path in layer.paths:
                    if not hasattr(glyph_path, 'nodes') or not glyph_path.nodes:
                        continue
                    nodes = list(glyph_path.nodes)
                    point_count = len(nodes)
                    for i in range(point_count):
                        node = nodes[i]
                        if i == 0:
                            path.moveToPoint_((node.x, node.y))
                        elif node.type == GSLINE:
                            path.lineToPoint_((node.x, node.y))
                        elif node.type == GSCURVE:
                            if i + 2 < point_count and nodes[i+1].type == GSOFFCURVE and nodes[i+2].type == GSOFFCURVE:
                                cp1 = nodes[i+1]
                                cp2 = nodes[i+2]
                                end = nodes[i+3] if i+3 < point_count else node
                                path.curveToPoint_controlPoint1_controlPoint2_(
                                    (end.x, end.y), (cp1.x, cp1.y), (cp2.x, cp2.y))
                    if glyph_path.closed:
                        path.closePath()
            
            if path.elementCount() > 0:
                self.cachedPath = path
                self.cachedLayer = layer
                return path
            
            return None
        except Exception as e:
            print(f"❌ ERROR in buildPathFromLayer: {e}")
            return None

    # Draw functions (simplified from original)
    def drawRect_(self, rect):
        try:
            # Clear background
            NSColor.whiteColor().set()
            NSBezierPath.fillRect_(self.bounds())
            NSColor.grayColor().set()
            NSBezierPath.strokeRect_(NSInsetRect(self.bounds(), 1, 1))
            
            if not self.metrics:
                self._drawMessage("No metrics available")
                return
            
            current_master = self.getCurrentMaster()
            if not current_master:
                self._drawMessage("No master available")
                return
            
            # Get and draw the glyph
            layer = self.getCurrentLayer()
            if not layer:
                self._drawMessage("No glyph layer")
                return
            
            glyphPath = self.buildPathFromLayer(layer)
            if not glyphPath:
                self._drawMessage("No path data")
                return
            
            # Setup transformation
            w = self.bounds().size.width
            h = self.bounds().size.height
            asc = float(current_master.ascender)
            desc = float(current_master.descender)
            padding = 20.0
            available_height = h - 2 * padding
            total_height = asc - desc
            if total_height <= 0:
                total_height = 1000.0
            scale = available_height / total_height
            view_baseline = padding + (-desc * scale)
            layerWidth = float(layer.width)
            x_padding = (w - (layerWidth * scale)) / 2.0
            
            # Draw metrics lines
            self._drawMetrics(current_master, scale, view_baseline, w, h)
            
            # Draw beams if enabled
            if self.showXbeam:
                self._drawXbeam(current_master, scale, view_baseline, w, h)
            
            if self.showYbeam:
                self._drawYbeam(layer, scale, view_baseline, x_padding, w, h)
            
            # Draw the glyph
            transform = NSAffineTransform.transform()
            transform.translateXBy_yBy_(x_padding, view_baseline)
            transform.scaleXBy_yBy_(scale, scale)
            transformedPath = glyphPath.copy()
            transformedPath.transformUsingAffineTransform_(transform)
            NSColor.blackColor().set()
            transformedPath.fill()
            
        except Exception as e:
            print(f"❌ ERROR in drawRect: {e}")
            self._drawMessage("Display error")

    @objc.python_method
    def _drawMetrics(self, master, scale, view_baseline, w, h):
        """Draw metric lines (ascender, x-height, baseline, descender)"""
        asc = float(master.ascender)
        xh = float(master.xHeight)
        desc = float(master.descender)
        cap = float(getattr(master, 'capHeight', 700))
        
        gray_color = NSColor.grayColor().colorWithAlphaComponent_(0.5)
        lines = [
            (view_baseline + (asc * scale), f"Asc ({int(asc)})", gray_color),
            (view_baseline + (cap * scale), f"Cap ({int(cap)})", gray_color),
            (view_baseline + (xh * scale), f"xH ({int(xh)})", gray_color),
            (view_baseline, "Base (0)", gray_color),
            (view_baseline + (desc * scale), f"Desc ({int(desc)})", gray_color)
        ]
        
        for y_pos, label, color in lines:
            if 0 <= y_pos <= h:
                color.set()
                line_path = NSBezierPath.bezierPath()
                line_path.moveToPoint_((10, y_pos))
                line_path.lineToPoint_((w - 10, y_pos))
                line_path.setLineWidth_(1.0)
                line_path.stroke()
                
                fontLabel = NSFont.systemFontOfSize_(9)
                attrs = {NSFontAttributeName: fontLabel, NSForegroundColorAttributeName: color}
                NSAttributedString.alloc().initWithString_attributes_(label, attrs).drawAtPoint_((5, y_pos + 2))

    @objc.python_method
    def _drawXbeam(self, master, scale, view_baseline, w, h):
        """Draw horizontal measurement beam"""
        xbeam_y = view_baseline + (self.xbeamPosition * scale)
        if 0 <= xbeam_y <= h:
            NSColor.blueColor().colorWithAlphaComponent_(0.7).set()
            xbeam_path = NSBezierPath.bezierPath()
            xbeam_path.moveToPoint_((10, xbeam_y))
            xbeam_path.lineToPoint_((w - 10, xbeam_y))
            xbeam_path.setLineWidth_(2.0)
            dash_pattern = [4, 2]
            xbeam_path.setLineDash_count_phase_(dash_pattern, len(dash_pattern), 0)
            xbeam_path.stroke()
            
            fontLabel = NSFont.systemFontOfSize_(9)
            attrs = {NSFontAttributeName: fontLabel, NSForegroundColorAttributeName: NSColor.blueColor()}
            label_text = f"Xbeam: {self.xbeamPosition}"
            NSAttributedString.alloc().initWithString_attributes_(label_text, attrs).drawAtPoint_((w - 110, xbeam_y + 2))

    @objc.python_method
    def _drawYbeam(self, layer, scale, view_baseline, x_padding, w, h):
        """Draw vertical measurement beam"""
        ybeam_x = x_padding + (self.ybeamPosition * scale)
        if 0 <= ybeam_x <= w:
            NSColor.greenColor().colorWithAlphaComponent_(0.7).set()
            ybeam_path = NSBezierPath.bezierPath()
            ybeam_path.moveToPoint_((ybeam_x, 10))
            ybeam_path.lineToPoint_((ybeam_x, h - 10))
            ybeam_path.setLineWidth_(2.0)
            dash_pattern = [4, 2]
            ybeam_path.setLineDash_count_phase_(dash_pattern, len(dash_pattern), 0)
            ybeam_path.stroke()
            
            fontLabel = NSFont.systemFontOfSize_(9)
            attrs = {NSFontAttributeName: fontLabel, NSForegroundColorAttributeName: NSColor.greenColor()}
            label_text = f"Ybeam: {self.ybeamPosition}"
            NSAttributedString.alloc().initWithString_attributes_(label_text, attrs).drawAtPoint_((ybeam_x + 5, h - 20))

    @objc.python_method
    def _drawMessage(self, message):
        w = self.bounds().size.width
        h = self.bounds().size.height
        font = NSFont.systemFontOfSize_(12)
        attrs = {
            NSFontAttributeName: font,
            NSForegroundColorAttributeName: NSColor.grayColor()
        }
        msg_str = NSAttributedString.alloc().initWithString_attributes_(message, attrs)
        msg_size = msg_str.size()
        x = (w - msg_size.width) / 2
        y = (h - msg_size.height) / 2
        msg_str.drawAtPoint_((x, y))

# Wrapper class
class EnhancedPreviewWrapper(object):
    def __init__(self, posSize):
        self.view = EnhancedPreviewView.alloc().initWithFrame_(((0, 0), (posSize[2], posSize[3])))
        self._nsObject = self.view

    def getNSView(self):
        return self._nsObject

    def setCharacter(self, ch):
        self.view.setCharacter_(ch)

    def setMetrics(self, metrics):
        self.view.setMetrics_(metrics)
        
    def setXbeamPosition(self, position):
        self.view.setXbeamPosition_(position)
        
    def setYbeamPosition(self, position):
        self.view.setYbeamPosition_(position)
        
    def setShowXbeam(self, show):
        self.view.setShowXbeam_(show)
        
    def setShowYbeam(self, show):
        self.view.setShowYbeam_(show)
        
    def setAxisValues(self, axisValues):
        self.view.setAxisValues_(axisValues)

# CocoaViewWrapper class
class CocoaViewWrapper(VanillaBaseObject):
    def __init__(self, posSize, nsView):
        self._posSize = posSize
        self._nsObject = nsView

    def getNSView(self):
        return self._nsObject

# Main panel class
class EnhancedGlyphPreviewPanel(object):
    def __init__(self):
        try:
            self.font = Glyphs.font
            if not self.font:
                Message("No Font Open", "Please open a font first")
                return

            # Get axes information
            self.axes = self.getRealAxes()
            num_axes = len(self.axes)
            
            total_height = 200 + (num_axes * 160)  # Increased height for both sides
            self.w = Window((1120, total_height), "Intermediate Glyphs Maker with Continuous Preview")

            # Titles
            self.w.leftTitle = TextBox((20, 15, 500, 22), 
                                     "Left: Master Reference (check 'Hide' to exclude axis from interpolation)", 
                                     sizeStyle="small")
            self.w.rightTitle = TextBox((570, 15, 500, 22), 
                                      "Right: Continuous Preview (check 'Hide' to exclude axis)", 
                                      sizeStyle="small")

            # Character inputs
            self.w.leftChar = EditText((20, 40, 50, 22), "H", callback=self.updateLeft)
            self.w.rightChar = EditText((570, 40, 50, 22), "H", callback=self.updateRight)

            # Master selector
            masters = [m.name for m in self.font.masters]
            self.w.masterLabel = TextBox((20, 70, 50, 22), "Master:")
            self.w.masterPopup = PopUpButton((70, 70, 200, 22), masters, callback=self.masterChanged)

            y_position = 100
            
            # LEFT CONTROLS (with axes and hide checkboxes)
            self.w.leftXbeamLabel = TextBox((20, y_position, 80, 22), "Xbeam:")
            self.w.leftXbeamSlider = Slider((100, y_position, 120, 22), 
                                          minValue=-200, maxValue=1000, value=520, 
                                          callback=self.leftXbeamChanged)
            self.w.leftXbeamValue = EditText((230, y_position, 40, 22), "520", 
                                           callback=self.leftXbeamValueChanged)
            self.w.leftXbeamHide = CheckBox((275, y_position, 60, 22), "Hide", 
                                          callback=self.leftXbeamHideChanged)

            y_position += 30

            self.w.leftYbeamLabel = TextBox((20, y_position, 80, 22), "Ybeam:")
            self.w.leftYbeamSlider = Slider((100, y_position, 120, 22), 
                                          minValue=0, maxValue=1000, value=300, 
                                          callback=self.leftYbeamChanged)
            self.w.leftYbeamValue = EditText((230, y_position, 40, 22), "300", 
                                           callback=self.leftYbeamValueChanged)
            self.w.leftYbeamHide = CheckBox((275, y_position, 60, 22), "Hide", 
                                          callback=self.leftYbeamHideChanged)

            y_position += 40

            # LEFT AXES (with sliders and hide checkboxes)
            self.left_axes = {}
            self.left_axis_value_fields = {}
            self.left_axis_hide_checkboxes = {}
            
            if self.axes:
                for i, axis in enumerate(self.axes):
                    setattr(self.w, f"leftAxisLabel_{i}", TextBox((20, y_position, 80, 22), f"{axis['name']}:"))
                    setattr(self.w, f"leftAxisSlider_{i}", 
                            Slider((100, y_position, 120, 22),
                                  minValue=axis['minValue'], maxValue=axis['maxValue'], 
                                  value=axis['defaultValue'], callback=self.leftAxisChanged))
                    
                    axis_field = EditText((230, y_position, 40, 22), f"{int(axis['defaultValue'])}",
                                        callback=self.leftAxisValueChanged)
                    setattr(self.w, f"leftAxisValue_{i}", axis_field)
                    
                    # HIDE CHECKBOX FOR LEFT AXIS
                    hide_checkbox = CheckBox((275, y_position, 60, 22), "Hide",
                                           callback=self.leftAxisHideChanged)
                    setattr(self.w, f"leftAxisHide_{i}", hide_checkbox)
                    
                    self.left_axis_value_fields[i] = axis_field
                    self.left_axis_hide_checkboxes[i] = hide_checkbox
                    self.left_axes[i] = axis
                    y_position += 30

            # RIGHT CONTROLS
            right_y_position = 100
            
            self.w.rightXbeamLabel = TextBox((570, right_y_position, 80, 22), "Xbeam:")
            self.w.rightXbeamSlider = Slider((650, right_y_position, 120, 22), 
                                           minValue=-200, maxValue=1000, value=520, 
                                           callback=self.rightXbeamChanged)
            self.w.rightXbeamValue = EditText((780, right_y_position, 40, 22), "520",
                                            callback=self.rightXbeamValueChanged)
            self.w.rightXbeamHide = CheckBox((825, right_y_position, 60, 22), "Hide", 
                                           callback=self.rightXbeamHideChanged)

            right_y_position += 30

            self.w.rightYbeamLabel = TextBox((570, right_y_position, 80, 22), "Ybeam:")
            self.w.rightYbeamSlider = Slider((650, right_y_position, 120, 22), 
                                           minValue=0, maxValue=1000, value=300, 
                                           callback=self.rightYbeamChanged)
            self.w.rightYbeamValue = EditText((780, right_y_position, 40, 22), "300",
                                            callback=self.rightYbeamValueChanged)
            self.w.rightYbeamHide = CheckBox((825, right_y_position, 60, 22), "Hide", 
                                           callback=self.rightYbeamHideChanged)

            right_y_position += 40

            # RIGHT AXES (with sliders for interpolation and Hide checkboxes)
            self.right_axes = {}
            self.right_axis_value_fields = {}
            self.right_axis_hide_checkboxes = {}
            
            if self.axes:
                for i, axis in enumerate(self.axes):
                    setattr(self.w, f"rightAxisLabel_{i}", TextBox((570, right_y_position, 80, 22), f"{axis['name']}:"))
                    setattr(self.w, f"rightAxisSlider_{i}", 
                            Slider((650, right_y_position, 120, 22),
                                  minValue=axis['minValue'], maxValue=axis['maxValue'], 
                                  value=axis['defaultValue'], callback=self.rightAxisChanged))
                    
                    axis_field = EditText((780, right_y_position, 40, 22), f"{int(axis['defaultValue'])}",
                                        callback=self.rightAxisValueChanged)
                    setattr(self.w, f"rightAxisValue_{i}", axis_field)
                    
                    # HIDE CHECKBOX FOR RIGHT AXIS
                    hide_checkbox = CheckBox((825, right_y_position, 60, 22), "Hide",
                                           callback=self.rightAxisHideChanged)
                    setattr(self.w, f"rightAxisHide_{i}", hide_checkbox)
                    
                    self.right_axis_value_fields[i] = axis_field
                    self.right_axis_hide_checkboxes[i] = hide_checkbox
                    self.right_axes[i] = axis
                    right_y_position += 30

            # PREVIEW AREAS
            preview_y = max(y_position, right_y_position) + 20
            preview_height = 350
            
            self.leftPreview = EnhancedPreviewWrapper((20, preview_y, 530, preview_height))
            self.rightPreview = EnhancedPreviewWrapper((570, preview_y, 530, preview_height))

            self.w.leftPreview = CocoaViewWrapper((20, preview_y, 530, preview_height), self.leftPreview.getNSView())
            self.w.rightPreview = CocoaViewWrapper((570, preview_y, 530, preview_height), self.rightPreview.getNSView())

            # BUTTONS
            button_y = preview_y + preview_height + 10
            
            # Left side button removed (Debug button)
            
            self.w.createLayerButton = Button((570, button_y, 230, 24), 
                                            "Create intermediate layer", 
                                            callback=self.createIntermediateLayer)
            
            self.w.refreshButton = Button((810, button_y, 120, 24), 
                                        "Refresh Preview", 
                                        callback=self.refreshPreview)
            
            self.w.webPreviewButton = Button((940, button_y, 150, 24), 
                                           "Preview in Web Browser", 
                                           callback=self.webPreview)

            print("🎉 Panel initialized successfully")
            print(f"📊 Axes detected: {len(self.axes)}")

            self.setMaster(0)
            self.w.open()

        except Exception as e:
            print(f"❌ ERROR initializing panel: {e}")
            import traceback
            traceback.print_exc()
            Message("Error", "Failed to initialize panel")

    @objc.python_method
    def getRealAxes(self):
        axes = []
        try:
            font = Glyphs.font
            if font and hasattr(font, 'axes'):
                for idx, axis in enumerate(font.axes):
                    master_values = [m.axes[idx] for m in font.masters]
                    min_val = min(master_values)
                    max_val = max(master_values)
                    default_val = master_values[0] if master_values else min_val
                    
                    # Get axis name and tag
                    axis_name = getattr(axis, "name", f"Axis {idx+1}")
                    axis_tag = getattr(axis, "axisTag", "")
                    
                    axes.append({
                        'name': axis_name,
                        'tag': axis_tag,
                        'minValue': min_val,
                        'maxValue': max_val,
                        'defaultValue': default_val
                    })
                    
                    print(f"[Panel] Found axis: {axis_name} (tag: {axis_tag}), range: {min_val}-{max_val}, default: {default_val}")
        except Exception as e:
            print(f"❌ Error getting axes: {e}")
        return axes

    # Callback methods
    def updateLeft(self, sender=None):
        ch = self.w.leftChar.get().strip()
        self.leftPreview.setCharacter(ch)

    def updateRight(self, sender=None):
        ch = self.w.rightChar.get().strip()
        self.rightPreview.setCharacter(ch)

    def masterChanged(self, sender=None):
        idx = self.w.masterPopup.get()
        self.setMaster(idx)





    @objc.python_method
    def setMaster(self, index):
        try:
            master = self.font.masters[index]
            metrics = {
                'masterID': master.id,
                'masterIndex': index,
                'asc': float(master.ascender),
                'desc': float(master.descender),
                'xh': float(master.xHeight),
            }
            
            # Set metrics for both previews
            self.leftPreview.setMetrics(metrics)
            self.rightPreview.setMetrics(metrics)
            
            # Update Xbeam to x-height
            desc = int(master.descender)
            asc = int(master.ascender)
            xh = int(master.xHeight)
            
            self.w.leftXbeamSlider.set(xh)
            self.w.leftXbeamValue.set(str(xh))
            self.w.rightXbeamSlider.set(xh)
            self.w.rightXbeamValue.set(str(xh))

            # Update left axis sliders to match master
            for i, axis in enumerate(self.axes):
                axis_slider = getattr(self.w, f"leftAxisSlider_{i}")
                axis_value = getattr(self.w, f"leftAxisValue_{i}")
                master_axis_value = master.axes[i]
                axis_slider.set(master_axis_value)
                axis_value.set(f"{int(master_axis_value)}")
                
                # Update right axis sliders to match master
                axis_slider_right = getattr(self.w, f"rightAxisSlider_{i}")
                axis_value_right = getattr(self.w, f"rightAxisValue_{i}")
                axis_slider_right.set(master_axis_value)
                axis_value_right.set(f"{int(master_axis_value)}")
                
            # Update the previews
            self.updateLeftAxes()
            self.updateRightAxes()

        except Exception as e:
            print(f"❌ Error in setMaster: {e}")

    # Left side callbacks
    def leftXbeamChanged(self, sender=None):
        val = self.w.leftXbeamSlider.get()
        self.w.leftXbeamValue.set(str(int(val)))
        self.leftPreview.setXbeamPosition(val)

    def leftYbeamChanged(self, sender=None):
        val = self.w.leftYbeamSlider.get()
        self.w.leftYbeamValue.set(str(int(val)))
        self.leftPreview.setYbeamPosition(val)
        
    def leftXbeamHideChanged(self, sender=None):
        hide = self.w.leftXbeamHide.get()
        self.leftPreview.setShowXbeam(not hide)
        
    def leftYbeamHideChanged(self, sender=None):
        hide = self.w.leftYbeamHide.get()
        self.leftPreview.setShowYbeam(not hide)
        
    def leftXbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.leftXbeamValue.get().strip()
            if value_str:
                value = float(value_str)
                master = self.font.masters[self.w.masterPopup.get()]
                desc = int(master.descender)
                asc = int(master.ascender)
                value = max(desc, min(value, asc))
                self.w.leftXbeamSlider.set(value)
                self.w.leftXbeamValue.set(str(int(value)))
                self.leftPreview.setXbeamPosition(value)
        except ValueError:
            current_val = self.w.leftXbeamSlider.get()
            self.w.leftXbeamValue.set(str(int(current_val)))

    def leftYbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.leftYbeamValue.get().strip()
            if value_str:
                value = float(value_str)
                # Get current layer to check max width
                metrics = {
                    'masterID': self.font.masters[self.w.masterPopup.get()].id,
                    'masterIndex': self.w.masterPopup.get()
                }
                self.leftPreview.setMetrics(metrics)
                self.leftPreview.view.metrics = metrics
                layer = self.leftPreview.view.getCurrentLayer()
                max_width = int(layer.width) if layer else 1000
                value = max(0, min(value, max_width))
                self.w.leftYbeamSlider.set(value)
                self.w.leftYbeamValue.set(str(int(value)))
                self.leftPreview.setYbeamPosition(value)
        except ValueError:
            current_val = self.w.leftYbeamSlider.get()
            self.w.leftYbeamValue.set(str(int(current_val)))
    
    def leftAxisChanged(self, sender=None):
        self.updateLeftAxes()
        
    def leftAxisValueChanged(self, sender=None):
        from time import sleep
        sleep(0.05)
        try:
            for i, axis_field in self.left_axis_value_fields.items():
                if sender == axis_field:
                    value_str = axis_field.get().strip()
                    if value_str:
                        try:
                            value = float(value_str)
                            axis_info = self.left_axes[i]
                            value = max(axis_info['minValue'], min(value, axis_info['maxValue']))
                            axis_slider = getattr(self.w, f"leftAxisSlider_{i}")
                            axis_slider.set(value)
                            axis_field.set(str(int(value)))
                            self.updateLeftAxes()
                        except ValueError:
                            axis_slider = getattr(self.w, f"leftAxisSlider_{i}")
                            current_val = axis_slider.get()
                            axis_field.set(str(int(current_val)))
                    else:
                        axis_slider = getattr(self.w, f"leftAxisSlider_{i}")
                        current_val = axis_slider.get()
                        axis_field.set(str(int(current_val)))
                    break
        except Exception as e:
            print(f"❌ Error in leftAxisValueChanged: {e}")
    
    def leftAxisHideChanged(self, sender=None):
        """Handle when a left axis Hide checkbox is toggled"""
        try:
            # Find which checkbox was toggled
            for i, checkbox in self.left_axis_hide_checkboxes.items():
                if sender == checkbox:
                    hide_state = checkbox.get()
                    axis_info = self.left_axes[i]
                    axis_name = axis_info['name']
                    
                    print(f"[Left Axis Hide] Axis '{axis_name}' hide state: {hide_state}")
                    
                    # Update the preview with new axis values
                    self.updateLeftAxes()
                    break
        except Exception as e:
            print(f"❌ Error in leftAxisHideChanged: {e}")

    # Right side callbacks
    def rightXbeamChanged(self, sender=None):
        val = self.w.rightXbeamSlider.get()
        self.w.rightXbeamValue.set(str(int(val)))
        self.rightPreview.setXbeamPosition(val)

    def rightYbeamChanged(self, sender=None):
        val = self.w.rightYbeamSlider.get()
        self.w.rightYbeamValue.set(str(int(val)))
        self.rightPreview.setYbeamPosition(val)
        
    def rightXbeamHideChanged(self, sender=None):
        hide = self.w.rightXbeamHide.get()
        self.rightPreview.setShowXbeam(not hide)
        
    def rightYbeamHideChanged(self, sender=None):
        hide = self.w.rightYbeamHide.get()
        self.rightPreview.setShowYbeam(not hide)
        
    def rightXbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.rightXbeamValue.get().strip()
            if value_str:
                value = float(value_str)
                master = self.font.masters[self.w.masterPopup.get()]
                desc = int(master.descender)
                asc = int(master.ascender)
                value = max(desc, min(value, asc))
                self.w.rightXbeamSlider.set(value)
                self.w.rightXbeamValue.set(str(int(value)))
                self.rightPreview.setXbeamPosition(value)
        except ValueError:
            current_val = self.w.rightXbeamSlider.get()
            self.w.rightXbeamValue.set(str(int(current_val)))
            
    def rightYbeamValueChanged(self, sender=None):
        try:
            value_str = self.w.rightYbeamValue.get().strip()
            if value_str:
                value = float(value_str)
                # Get current layer to check max width
                metrics = {
                    'masterID': self.font.masters[self.w.masterPopup.get()].id,
                    'masterIndex': self.w.masterPopup.get()
                }
                self.rightPreview.setMetrics(metrics)
                self.rightPreview.view.metrics = metrics
                layer = self.rightPreview.view.getCurrentLayer()
                max_width = int(layer.width) if layer else 1000
                value = max(0, min(value, max_width))
                self.w.rightYbeamSlider.set(value)
                self.w.rightYbeamValue.set(str(int(value)))
                self.rightPreview.setYbeamPosition(value)
        except ValueError:
            current_val = self.w.rightYbeamSlider.get()
            self.w.rightYbeamValue.set(str(int(current_val)))
    
    def rightAxisChanged(self, sender=None):
        self.updateRightAxes()
        
    def rightAxisValueChanged(self, sender=None):
        from time import sleep
        sleep(0.05)
        try:
            for i, axis_field in self.right_axis_value_fields.items():
                if sender == axis_field:
                    value_str = axis_field.get().strip()
                    if value_str:
                        try:
                            value = float(value_str)
                            axis_info = self.right_axes[i]
                            value = max(axis_info['minValue'], min(value, axis_info['maxValue']))
                            axis_slider = getattr(self.w, f"rightAxisSlider_{i}")
                            axis_slider.set(value)
                            axis_field.set(str(int(value)))
                            self.updateRightAxes()
                        except ValueError:
                            axis_slider = getattr(self.w, f"rightAxisSlider_{i}")
                            current_val = axis_slider.get()
                            axis_field.set(str(int(current_val)))
                    else:
                        axis_slider = getattr(self.w, f"rightAxisSlider_{i}")
                        current_val = axis_slider.get()
                        axis_field.set(str(int(current_val)))
                    break
        except Exception as e:
            print(f"❌ Error in rightAxisValueChanged: {e}")
    
    def rightAxisHideChanged(self, sender=None):
        """Handle when a right axis Hide checkbox is toggled"""
        try:
            # Find which checkbox was toggled
            for i, checkbox in self.right_axis_hide_checkboxes.items():
                if sender == checkbox:
                    hide_state = checkbox.get()
                    axis_info = self.right_axes[i]
                    axis_name = axis_info['name']
                    
                    print(f"[Right Axis Hide] Axis '{axis_name}' hide state: {hide_state}")
                    
                    # Update the preview with new axis values
                    self.updateRightAxes()
                    break
        except Exception as e:
            print(f"❌ Error in rightAxisHideChanged: {e}")
    
    def updateLeftAxes(self):
        """Left side uses slider values (with hide functionality)"""
        axisValues = {}
        
        for i, axis in enumerate(self.axes):
            slider = getattr(self.w, f"leftAxisSlider_{i}")
            value_label = getattr(self.w, f"leftAxisValue_{i}")
            value = slider.get()
            axis_name = axis['name']
            
            # Check if this axis is hidden
            is_hidden = False
            if i in self.left_axis_hide_checkboxes:
                is_hidden = self.left_axis_hide_checkboxes[i].get()
            
            if not is_hidden:
                # Only include axis if it's NOT hidden
                axisValues[axis_name.lower()] = value
                
                # Also store common axis tags if applicable
                axis_lower = axis_name.lower()
                if 'weight' in axis_lower or 'wght' in axis_lower:
                    axisValues['weight'] = value
                    axisValues['wght'] = value
                elif 'width' in axis_lower or 'wdth' in axis_lower:
                    axisValues['width'] = value
                    axisValues['wdth'] = value
                elif 'optical' in axis_lower or 'opsz' in axis_lower:
                    axisValues['optical'] = value
                    axisValues['opsz'] = value
                elif 'italic' in axis_lower or 'ital' in axis_lower:
                    axisValues['italic'] = value
                    axisValues['ital'] = value
                elif 'slant' in axis_lower or 'slnt' in axis_lower:
                    axisValues['slant'] = value
                    axisValues['slnt'] = value
            
            # Update the value field display
            value_label.set(f"{int(value)}")
            
            # Visual feedback for hidden axes (gray out the slider)
            slider.enable(not is_hidden)
            value_label.enable(not is_hidden)
            
            # Update checkbox label color for visual feedback
            checkbox = getattr(self.w, f"leftAxisHide_{i}")
            if hasattr(checkbox, 'setTitleColor_'):
                if is_hidden:
                    checkbox.setTitleColor_(NSColor.grayColor())
                else:
                    checkbox.setTitleColor_(NSColor.blackColor())
        
        print(f"[Panel] Updated left axis values: {axisValues}")
        self.leftPreview.setAxisValues(axisValues)
        
    def updateRightAxes(self):
        """Right side uses slider values for interpolation, respecting Hide checkboxes"""
        axisValues = {}
        for i, axis in enumerate(self.axes):
            slider = getattr(self.w, f"rightAxisSlider_{i}")
            value_label = getattr(self.w, f"rightAxisValue_{i}")
            value = slider.get()
            axis_name = axis['name']
            
            # Check if this axis is hidden
            is_hidden = False
            if i in self.right_axis_hide_checkboxes:
                is_hidden = self.right_axis_hide_checkboxes[i].get()
            
            if not is_hidden:
                # Only include axis if it's NOT hidden
                axisValues[axis_name.lower()] = value
                
                # Also store common axis tags if applicable
                axis_lower = axis_name.lower()
                if 'weight' in axis_lower or 'wght' in axis_lower:
                    axisValues['weight'] = value
                    axisValues['wght'] = value
                elif 'width' in axis_lower or 'wdth' in axis_lower:
                    axisValues['width'] = value
                    axisValues['wdth'] = value
                elif 'optical' in axis_lower or 'opsz' in axis_lower:
                    axisValues['optical'] = value
                    axisValues['opsz'] = value
                elif 'italic' in axis_lower or 'ital' in axis_lower:
                    axisValues['italic'] = value
                    axisValues['ital'] = value
                elif 'slant' in axis_lower or 'slnt' in axis_lower:
                    axisValues['slant'] = value
                    axisValues['slnt'] = value
            
            # Update the value field display
            value_label.set(f"{int(value)}")
            
            # Visual feedback for hidden axes (gray out the slider)
            slider.enable(not is_hidden)
            value_label.enable(not is_hidden)
            
            # Update checkbox label color for visual feedback
            checkbox = getattr(self.w, f"rightAxisHide_{i}")
            if hasattr(checkbox, 'setTitleColor_'):
                if is_hidden:
                    checkbox.setTitleColor_(NSColor.grayColor())
                else:
                    checkbox.setTitleColor_(NSColor.blackColor())
        
        print(f"[Panel] Updated right axis values: {axisValues}")
        self.rightPreview.setAxisValues(axisValues)
        
        # Store for web preview
        self.current_axis_values = axisValues

    def refreshPreview(self, sender=None):
        """Refresh both previews and ensure they're up to date"""
        try:
            # Update characters
            self.updateLeft()
            self.updateRight()
        
            # Update axis values
            self.updateLeftAxes()
            self.updateRightAxes()
        
            # Force redraw
            self.leftPreview.view.setNeedsDisplay_(True)
            self.rightPreview.view.setNeedsDisplay_(True)
        
            print("✅ Preview refreshed")
        except Exception as e:
            print(f"❌ Error in refreshPreview: {e}")
    def webPreview(self, sender=None):
        """Create and open interactive web browser preview"""
        try:
            # Crear HTML en carpeta de Descargas
            downloads_dir = os.path.expanduser("~/Downloads")
            if not os.path.exists(downloads_dir):
                downloads_dir = tempfile.gettempdir()
            
            # Obtener la fuente actual
            font = Glyphs.font
            if not font:
                print("❌ No hay fuente abierta")
                return
            
            # Obtener nombre de la fuente
            font_name = otVarFullName(font)
            
            print(f"🛠 Creando HTML de prueba en: {downloads_dir}")
            print(f"   Fuente: {font_name}")
            
            # Crear el HTML usando la función del script web type intermediate.py
            html_path = createHTMLTest(font_name, downloads_dir)
            
            if html_path:
                print(f"✅ HTML creado exitosamente: {html_path}")
                
                # Abrir el HTML en el navegador
                try:
                    webbrowser.open('file://' + html_path)
                    print(f"🌐 HTML abierto en el navegador")
                except Exception as e:
                    print(f"⚠️ No se pudo abrir en el navegador: {e}")
                    print(f"📄 Archivo disponible en: {html_path}")
            else:
                print("❌ No se pudo crear el HTML de prueba")
            
        except Exception as e:
            print(f"❌ Error en webPreview: {e}")
            import traceback
            traceback.print_exc()

    def createIntermediateLayer(self, sender):
        """Create an intermediate layer with the current axis values from the right preview"""
        font = Glyphs.font
        if not font or not font.selectedLayers:
            Message("No glyph selected", "Error")
            return

        # Get current axis values from right preview
        if not hasattr(self, 'current_axis_values') or not self.current_axis_values:
            Message("No axis values available. Adjust sliders first.", "Error")
            return
    
        # Build coordinates dictionary from current axis values
        coords_dict = {}
        for axis in font.axes:
            axis_name = axis.name
            axis_name_lower = axis_name.lower()
        
            # Try to find matching value in current_axis_values
            value = None
            for key, val in self.current_axis_values.items():
                if key.lower() == axis_name_lower:
                    value = val
                    break
        
            # Also check for common axis tags
            if value is None:
                axis_tag = getattr(axis, "axisTag", "").lower()
                if axis_tag in self.current_axis_values:
                    value = self.current_axis_values[axis_tag]
                elif axis_name_lower == "weight" and "wght" in self.current_axis_values:
                    value = self.current_axis_values["wght"]
                elif axis_name_lower == "width" and "wdth" in self.current_axis_values:
                    value = self.current_axis_values["wdth"]
        
            if value is not None:
                coords_dict[axis_name] = value
            else:
                # Use master value as fallback
                master = font.masters[self.w.masterPopup.get()]
                axis_index = list(font.axes).index(axis)
                coords_dict[axis_name] = master.axes[axis_index]
    
        if not coords_dict:
            Message("No valid axis values found", "Error")
            return
    
        font.disableUpdateInterface()
    
        try:
            for layer in font.selectedLayers:
                glyph = layer.parent
                master = layer.master
            
                # Check for duplicate layers
                duplicate_found = False
                for lyr in glyph.layers:
                    attrs = getattr(lyr, "attributes", {})
                    if isinstance(attrs, dict):
                        existing_coords = attrs.get("coordinates")
                        if isinstance(existing_coords, dict):
                            # Check if coordinates match
                            if all(
                                float(existing_coords.get(k, -9999)) == float(v)
                                for k, v in coords_dict.items()
                            ):
                                duplicate_found = True
                                Message(f"Layer with these coordinates already exists: {lyr.name}", "Warning")
                                break
            
                if duplicate_found:
                    continue
            
                # Create new layer WITHOUT undo to avoid the undo manager error
                newLayer = GSLayer()
                newLayer.associatedMasterId = master.id
            
                # Store coordinates in attributes
                newLayer.attributes["coordinates"] = coords_dict.copy()
            
                # Store interpolation info
                interp_coords = [float(coords_dict[a.name]) for a in font.axes]
                newLayer.attributes["interpolation"] = {
                    "coordinates": [str(v) for v in interp_coords],
                    "master": master.id,
                    "source": "intermediate_glyphs_maker"
                }
            
                newLayer.attributes["isSpecialLayer"] = True
            
                # Set layer name with brace notation
                newLayer.name = "{" + ",".join(str(round(v, 2)) for v in interp_coords) + "}"
            
                # Add to glyph
                glyph.layers.append(newLayer)
            
                # Now manually interpolate the layer
                success = self._interpolate_layer_manually(newLayer, font, glyph, coords_dict, master)
            
                if success:
                    print(f"✅ Created and interpolated layer: {newLayer.name} for glyph {glyph.name}")
                else:
                    print(f"⚠️ Created layer but interpolation failed: {newLayer.name}")
            
            # Refresh the preview
            self.refreshPreview()
            Message("Intermediate layer created successfully", "Success")
        
        except Exception as e:
            print(f"❌ Error in createIntermediateLayer: {e}")
            import traceback
            traceback.print_exc()
            Message(f"Error creating layer: {str(e)}", "Error")
        
        finally:
            font.enableUpdateInterface()
            
            
            
            
            
    def _interpolate_layer_manually(self, newLayer, font, glyph, target_coords, target_master):
        """Manually interpolate a layer using the font's interpolation engine"""
        try:
            # Method 1: Try using GSInstance
            try:
                # Create an instance with the target coordinates
                inst = GSInstance.alloc().init()
                inst.font = font
            
                # Build axis values in correct order
                axis_values = []
                for axis in font.axes:
                    axis_name = axis.name
                    if axis_name in target_coords:
                        axis_values.append(float(target_coords[axis_name]))
                    else:
                        # Use target master value
                        axis_index = list(font.axes).index(axis)
                        axis_values.append(float(target_master.axes[axis_index]))
            
                inst.axes = axis_values
            
                # Get interpolated font
                vf = inst.interpolatedFont
            
                if vf and glyph.name in vf.glyphs:
                    source_layer = vf.glyphs[glyph.name].layers[0]
                
                    # Copy paths from interpolated layer
                    if hasattr(source_layer, 'paths') and source_layer.paths:
                        # Clear existing paths
                        while len(newLayer.paths) > 0:
                            newLayer.paths.removeObjectAtIndex_(0)
                    
                        # Add new paths
                        for path in source_layer.paths:
                            new_path = path.copy()
                            newLayer.paths.append(new_path)
                
                    # Copy anchors
                    if hasattr(source_layer, 'anchors') and source_layer.anchors:
                        # Clear existing anchors
                        while len(newLayer.anchors) > 0:
                            newLayer.anchors.removeObjectAtIndex_(0)
                    
                        # Add new anchors
                        for anchor in source_layer.anchors:
                            new_anchor = anchor.copy()
                            newLayer.anchors.append(new_anchor)
                
                    # Copy components (for composite glyphs)
                    if hasattr(source_layer, 'components') and source_layer.components:
                        # Clear existing components
                        while len(newLayer.components) > 0:
                            newLayer.components.removeObjectAtIndex_(0)
                    
                        # Add new components
                        for component in source_layer.components:
                            new_component = component.copy()
                            newLayer.components.append(new_component)
                
                    # Copy width
                    if hasattr(source_layer, 'width'):
                        try:
                            newLayer.setWidth_(source_layer.width)
                        except:
                            try:
                                newLayer.width = source_layer.width
                            except:
                                pass
                
                    # Copy metrics if possible
                    if hasattr(source_layer, 'leftMetrics'):
                        try:
                            newLayer.setLeftMetrics_(source_layer.leftMetrics)
                        except:
                            pass
                
                    if hasattr(source_layer, 'rightMetrics'):
                        try:
                            newLayer.setRightMetrics_(source_layer.rightMetrics)
                        except:
                            pass
                
                    print(f"[Manual] Successfully interpolated via GSInstance with anchors")
                    return True
            except Exception as e:
                print(f"[Manual] GSInstance interpolation failed: {e}")
                import traceback
                traceback.print_exc()
        
            # Method 2: Use the font's built-in interpolation
            try:
                # Try to use the layer's reinterpolate method
                if hasattr(newLayer, 'reinterpolate'):
                    newLayer.reinterpolate()
                    print(f"[Manual] Used reinterpolate method")
                    return True
            except Exception as e:
                print(f"[Manual] reinterpolate failed: {e}")
        
            # Method 3: Find the two closest layers and interpolate between them
            layers_with_coords = []
        
            # Collect master layers
            for master in font.masters:
                for lyr in glyph.layers:
                    if hasattr(lyr, 'associatedMasterId') and lyr.associatedMasterId == master.id:
                        master_coords = {}
                        for axis in font.axes:
                            axis_index = list(font.axes).index(axis)
                            master_coords[axis.name] = master.axes[axis_index]
                        layers_with_coords.append((master_coords, lyr, master))
                        break
        
            # Collect existing brace layers
            for lyr in glyph.layers:
                vals = parse_brace_from_name(lyr)
                if vals:
                    try:
                        coords = {}
                        for i, axis in enumerate(font.axes):
                            if i < len(vals):
                                coords[axis.name] = vals[i]
                            else:
                                coords[axis.name] = 0.0
                        layers_with_coords.append((coords, lyr, None))
                    except Exception:
                        pass
        
            if len(layers_with_coords) >= 2:
                # Find closest two layers based on distance in axis space
                distances = []
                for coords, lyr, master in layers_with_coords:
                    distance = 0
                    for axis in font.axes:
                        axis_name = axis.name
                        target_val = target_coords.get(axis_name, 0)
                        source_val = coords.get(axis_name, 0)
                        distance += (target_val - source_val) ** 2
                    distance = math.sqrt(distance)
                    distances.append((distance, coords, lyr, master))
            
                distances.sort(key=lambda x: x[0])
            
                if len(distances) >= 2:
                    dist1, coords1, layer1, master1 = distances[0]
                    dist2, coords2, layer2, master2 = distances[1]
                
                    # Calculate interpolation factor
                    total_dist = dist1 + dist2
                    if total_dist > 0:
                        t = dist1 / total_dist
                    else:
                        t = 0.5
                
                    # Interpolate between the two closest layers
                    interp_layer = interpolate_layers_nodewise(layer1, layer2, t)
                
                    if interp_layer:
                        # Clear existing paths
                        while len(newLayer.paths) > 0:
                            newLayer.paths.removeObjectAtIndex_(0)
                    
                        # Copy interpolated paths
                        if hasattr(interp_layer, 'paths') and interp_layer.paths:
                            for path in interp_layer.paths:
                                new_path = path.copy()
                                newLayer.paths.append(new_path)
                    
                        # Interpolate anchors
                        if hasattr(layer1, 'anchors') and hasattr(layer2, 'anchors'):
                            anchors1 = layer1.anchors
                            anchors2 = layer2.anchors
                        
                            # Clear existing anchors
                            while len(newLayer.anchors) > 0:
                                newLayer.anchors.removeObjectAtIndex_(0)
                        
                            # Interpolate each anchor if they exist in both layers
                            if anchors1 and anchors2 and len(anchors1) == len(anchors2):
                                for i in range(len(anchors1)):
                                    anchor1 = anchors1[i]
                                    anchor2 = anchors2[i]
                                
                                    # Create new anchor
                                    new_anchor = anchor1.copy()
                                
                                    # Interpolate position
                                    ax = float(anchor1.position.x)
                                    ay = float(anchor1.position.y)
                                    bx = float(anchor2.position.x)
                                    by = float(anchor2.position.y)
                                
                                    new_anchor.position = NSPoint(ax + (bx - ax) * t, ay + (by - ay) * t)
                                
                                    newLayer.anchors.append(new_anchor)
                    
                        # Copy width
                        if hasattr(interp_layer, 'width'):
                            try:
                                newLayer.setWidth_(interp_layer.width)
                            except:
                                try:
                                    newLayer.width = interp_layer.width
                                except:
                                    pass
                    
                        print(f"[Manual] Successfully interpolated between two closest layers with anchors")
                        return True
        
            # Method 4: Just copy from the target master (fallback)
            target_master_layer = None
            for lyr in glyph.layers:
                if hasattr(lyr, 'associatedMasterId') and lyr.associatedMasterId == target_master.id:
                    target_master_layer = lyr
                    break
        
            if target_master_layer:
                # Clear existing paths
                while len(newLayer.paths) > 0:
                    newLayer.paths.removeObjectAtIndex_(0)
            
                # Copy paths
                if hasattr(target_master_layer, 'paths') and target_master_layer.paths:
                    for path in target_master_layer.paths:
                        new_path = path.copy()
                        newLayer.paths.append(new_path)
            
                # Copy anchors
                if hasattr(target_master_layer, 'anchors') and target_master_layer.anchors:
                    # Clear existing anchors
                    while len(newLayer.anchors) > 0:
                        newLayer.anchors.removeObjectAtIndex_(0)
                
                    # Add new anchors
                    for anchor in target_master_layer.anchors:
                        new_anchor = anchor.copy()
                        newLayer.anchors.append(new_anchor)
            
                # Copy width
                if hasattr(target_master_layer, 'width'):
                    try:
                        newLayer.setWidth_(target_master_layer.width)
                    except:
                        try:
                            newLayer.width = target_master_layer.width
                        except:
                            pass
            
                print(f"[Manual] Using target master layer as fallback with anchors")
                return True
        
            print("[Manual] All interpolation methods failed")
            return False
        
        except Exception as e:
            print(f"❌ Error in manual interpolation: {e}")
            import traceback
            traceback.print_exc()
            return False
            
            
            
            
            
# ---------------------------
# MAIN ENTRY POINT with singleton pattern
# ---------------------------
def main():
    global _panel_instance
    
    # Check if panel already exists
    if _panel_instance is not None:
        try:
            # Try to bring existing window to front
            _panel_instance.w.bringToFront()
            print("📌 Panel already exists, bringing to front")
            return
        except:
            # If that fails, create new instance
            _panel_instance = None
    
    try:
        # Create new panel instance
        _panel_instance = EnhancedGlyphPreviewPanel()
        
        # Set up cleanup when window closes
        def cleanup(sender=None):  # <-- ADDED sender parameter
            global _panel_instance
            _panel_instance = None
            print("🧹 Panel closed, instance cleaned up")
        
        if hasattr(_panel_instance, 'w'):
            _panel_instance.w.bind("close", cleanup)
            
    except Exception as e:
        print(f"❌ Error creating panel: {e}")
        import traceback
        traceback.print_exc()
        Message("Error", "Failed to create panel")

# Run the panel
if __name__ == "__main__":
    main()