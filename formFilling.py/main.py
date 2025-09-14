import datetime
import time
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import json
import os
st.title("गावानुसार अर्ज PDF तयार करा")

# Excel upload
uploaded_file = st.file_uploader("गावानुसार Excel डेटाबेस अपलोड करा.", type=["xlsx"])

if uploaded_file:

    df = pd.ExcelFile(uploaded_file)
    st.write("Records uploaded Successfully.")

    village_list = pd.read_excel(df, sheet_name="गाव")['गाव'].dropna().str.strip().unique()

    st.markdown("### 📋 अर्जासाठी माहिती भरा")

    # Use columns for layout
    col1, col2 = st.columns(2)

    with col1:
        vibhag = st.text_input("विभाग:", value="नाशिक पाटबंधारे विभाग, नाशिक")

        upvibhag = st.text_input("उपिवभाग:", value="नाशिक उजवा तट कालवा,नाशिक")

        upoffice = (upvibhag.split(",")[1] or "")
        upvibhag = upvibhag.split(",")[0]
        upofficer = st.text_input("उपिवभाग officer:", value="सहाय्यक अभियंता श्रेणी -१")

        taluka = st.text_input("तालुका:", value="इगतपुरी")

        jilha = st.text_input("जिल्हा:", value="नाशिक")


    with col2:
        jalashy = st.text_input(" पाण्याचे वाटप करणाऱ्या जलाशयाचे नाव:", value="दारणा जलाशय", disabled=True)

        shakha = st.text_input("शाखा:", value="दारणा धरण शाखा", disabled=True)

        je_name = st.text_input("शाखाधिकाऱ्याचे नाव:", value="यु.मु.महाले")

        start_date = st.date_input("📅 अर्ज करण्याची सुरुवातीची तारीख:", value=datetime.date.today())

        end_date = st.date_input("📅 अर्ज करण्याची शेवटची तारीख:", value=datetime.date.today())



    # Select village
    selected_village = st.selectbox("गाव निवडा", sorted(village_list))

    # Read data for selected village
    df = pd.read_excel(df, sheet_name=selected_village, dtype={"भुमापन क्रमांक": str, "पोट क्रमांक": str})

    # Forward-fill "name" to group null rows under last seen name
    df["group"] = df["अर्जदाराचे नाव"].ffill()

    # Sum tarea_int within each group
    df["mkarea_sum"] = df.groupby("group")["मालकीचे क्षेत्रफळ"].transform("sum")
    df["pmarea_sum"] = df.groupby("group")["पाणी मागणी क्षेत्र"].transform("sum")


    # Rename columns
    df = df.rename(columns={
        'भुमापन क्रमांक': 'no',
        'पोट क्रमांक': 'pno',
        'अर्जदाराचे नाव': 'name',
        'गावाचे नाव': 'village',
        'भुमापन क्र. किंवा पोट क्र.चे क्षेत्रफळ ': 'bsarea',
        'मालकीचे क्षेत्रफळ': 'mkarea',
        'पाणी मागणी क्षेत्र': 'pmarea',
        'पीक': 'crop',
        'mkarea_sum': 'mkarea_sum',
        'pmarea_sum': 'pmarea_sum'
    })


    def split_float_parts(value):
        try:
            formatted = f"{float(value):.2f}"
            int_part, frac_part = formatted.split('.')
        except:
            int_part, frac_part = '0', '00'
        return int_part, frac_part


    def convert_to_marathi_digits(text):
        if pd.isna(text):  # if value is NaN, just return it back
            return text
        eng_to_marathi = str.maketrans('0123456789', '०१२३४५६७८९')
        return str(text).translate(eng_to_marathi)


    df[['mkarea_sum_int', 'mkarea_sum_frac']] = df['mkarea_sum'].apply(lambda x: pd.Series(split_float_parts(x)))
    df[['pmarea_sum_int', 'pmarea_sum_frac']] = df['pmarea_sum'].apply(lambda x: pd.Series(split_float_parts(x)))
    df[['pmarea_int', 'pmarea_frac']] = df['pmarea'].apply(lambda x: pd.Series(split_float_parts(x)))
    df[['mkarea_int', 'mkarea_frac']] = df['mkarea'].apply(lambda x: pd.Series(split_float_parts(x)))
    df[['bsarea_int', 'bsarea_frac']] = df['bsarea'].apply(lambda x: pd.Series(split_float_parts(x)))

    df['no'] = df['no'].apply(convert_to_marathi_digits)
    df['pno'] = df['pno'].apply(convert_to_marathi_digits)
    df['pmarea_int'] = df['pmarea_int'].apply(convert_to_marathi_digits)
    df['pmarea_frac'] = df['pmarea_frac'].apply(convert_to_marathi_digits)
    df['mkarea_int'] = df['mkarea_int'].apply(convert_to_marathi_digits)
    df['mkarea_frac'] = df['mkarea_frac'].apply(convert_to_marathi_digits)
    df['bsarea_int'] = df['bsarea_int'].apply(convert_to_marathi_digits)
    df['bsarea_frac'] = df['bsarea_frac'].apply(convert_to_marathi_digits)
    df['pmarea_sum_int'] = df['pmarea_sum_int'].apply(convert_to_marathi_digits)
    df['pmarea_sum_frac'] = df['pmarea_sum_frac'].apply(convert_to_marathi_digits)
    df['mkarea_sum_int'] = df['mkarea_sum_int'].apply(convert_to_marathi_digits)
    df['mkarea_sum_frac'] = df['mkarea_sum_frac'].apply(convert_to_marathi_digits)

    condition = (
            (df["mkarea"].isna()) |
            ((df["mkarea_int"] == 0) & (df["mkarea_frac"] == 0))
    )

    df.loc[condition, ["mkarea_int", "mkarea_frac"]] = " "

    condition = (
            (df["bsarea"].isna()) |
            ((df["bsarea_int"] == 0) & (df["bsarea_frac"] == 0))
    )

    df.loc[condition, ["bsarea_int", "bsarea_frac"]] = " "


    def convert_to_marathi_date(date_obj):
        marathi_digits = str.maketrans('0123456789', '०१२३४५६७८९')
        return date_obj.strftime('%d/%m/%Y').translate(marathi_digits)


    start_date = convert_to_marathi_date(start_date)
    end_date = convert_to_marathi_date(end_date)

    data_json = df.to_dict(orient="records")

    # 📌 सर्व User Input dictionary मध्ये
    form_data = {
        "vibhag": vibhag,
        "upvibhag": upvibhag,
        "upoffice": upoffice,
        "upofficer": upofficer,
        "taluka": taluka,
        "jilha": jilha,
        "jalashy": jalashy,
        "shakha": shakha,
        "je_name": je_name,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "village": selected_village
    }




    # Path to font in project folder
    
    BASE_DIR = os.path.dirname(__file__)
    font_path = os.path.join(BASE_DIR, "fonts", "NotoSerifDevanagari-VariableFont_wdth,wght.ttf")


    with open(font_path, "rb") as f:
        import base64
        font_bytes = f.read()
        font_b64 = base64.b64encode(font_bytes).decode("utf-8")

    if st.button("Generate PDF") and font_b64:
        # Step 1 → Show spinner
        with st.spinner("PDF तयार होत आहे..."):
            time.sleep(2)  # simulate processing (replace with your PDF logic)

        # Step 2 → Show success message + Preview
        st.success("✅ PDF तयार झाला! खाली प्रीव्ह्यू पहा 👇")
        components.html(
            f"""
                    <html>
                    <head>
                      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/pdfmake.min.js"></script>
                      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.72/vfs_fonts.js"></script>
                    </head>
                    <body>
                      <button onclick="previewPDF()" 
                          style="padding:10px 15px; background:#2196F3; color:white; border:none; border-radius:6px; cursor:pointer; margin-right:10px;">
                         👁️ Preview PDF
                      </button>

                      <button onclick="downloadPDF()" 
                          style="padding:10px 15px; background:#4CAF50; color:white; border:none; border-radius:6px; cursor:pointer;">
                          ⬇️ Download PDF
                      </button>
                      <script>
                        const rows = {json.dumps(data_json, ensure_ascii=False)};
                        const form_data = {json.dumps(form_data, ensure_ascii=False)}

                        pdfMake.vfs["CustomFont.ttf"] = "{font_b64}";
                        pdfMake.fonts = {{
                            MarathiFont: {{
                                normal: "CustomFont.ttf",
                                bold: "CustomFont.ttf",
                                italics: "CustomFont.ttf",
                                bolditalics: "CustomFont.ttf"
                            }}
                        }};
                     var jlashypart = String(form_data.jalashy).split(" ");

                      var content = [];
                      for ( i = 0; i < rows.length; i++){{
                        row = rows[i];
if(row["name"]) {{  
                                                  
                       content.push({{
                        stack: [
                             {{
  table: {{
    widths: ['35%', '50%', '15%'],
    body: [[
      // First column (4 lines)
      {{
        stack: [
          {{ text: "शे.का.म.५,००,०००-७-०४-Az*-(टी)६५", fontSize: 10, lineHeight: 0.8 }},
          {{ text: "रा.नि.सा.बां.वि.क्र. २३५३२७, दिनांक ४-१-३४", fontSize: 10, lineHeight: 0.8 }},
          {{ text: "प्रा.प.,पा.वि.क्र.एफ एम एस-", fontSize: 10, lineHeight: 0.8 }},
          {{ text: "१०७९-२०१३ दि. १६-२-८१", fontSize: 10, lineHeight: 0.8 }}
        ]
      }},
      // Second column (4 lines)
      {{
        stack: [
          {{ text: "सा.यां.वि. ४९९ म.", fontSize: 10, decoration: "underline",lineHeight: 0.7, margin:[175,0,0,0]}},
          {{ text: "P.W.D. 449 M", fontSize: 10, lineHeight:0.7, margin:[175,0,0,0] }}, 
          {{ text: "पाटबंधारे विभाग", fontSize: 16, bold: true, lineHeight: 0.75,margin:[40,0,0,0] }},
          {{ text: "नमुना क्रमांक ७", fontSize: 12, bold: true, lineHeight: 1,margin:[50,0,0,0] }}
          
        ]
      }},
      // Third column (4 lines)
      {{
        stack: [
          {{ text: "१) पाटमोट संबंध नाही", fontSize: 10, lineHeight: 0.8 }},
          {{ text: "२) थकबाकीदार नाही", fontSize: 10, lineHeight: 0.8 }}, 
          {{ text: "३) ७/१२ घेतला आहे", fontSize: 10, lineHeight: 0.8 }},
          {{ text: "४) मंजुरीस हरकत नाही", fontSize: 10, lineHeight: 0.8 }}
          
        ]
      }}
    ]]
  }},
  layout: {{
    defaultBorder: false,
    paddingTop: function() {{ return 0; }},
    paddingBottom: function() {{ return 0; }}
  }}
}}, 

                            {{ text: "    ", fontSize: 6}},
                            {{ text: "जमीन ओलिताखाली आणण्यासाठी लागणाऱ्या पाण्याबद्दल सर्वसाधारण अर्ज", fontSize: 14,lineHeight: 0.7, margin: [110, 0, 0, 0], bold: true}},
                            {{ text: "    ", fontSize: 5}},
                            {{ text: [
                                     {{ text: "अर्ज क्रमांक                                                                                                                                             ", fontSize: 12}},
                                     {{ text: "कालवा निरीक्षक", fontSize: 12}},
                                 ],
                                 lineHeight: 0.7,
                                 }},
                            {{ text: "    ", fontSize: 7}},
                            {{ text: [
                                     {{ text: "कार्यकारी अभियंता  ", fontSize: 11}},
                                     {{ text: form_data.vibhag, fontSize: 12}},
                                     {{ text: "  विभाग यांस                                                                         ", fontSize: 11 }},
                                     {{ text: "(दुसरी प्रत", fontSize: 11 }},
                                 ],
                                 lineHeight: 0.7, margin: [3, 0, 0, 0]
                                 }}, 
                            {{ text: "    ", fontSize: 5}},    
                            {{ text: [
                                     {{ text: "  मी   ", fontSize: 10}},
                                     {{ text: (row["name"] || "") + "  ", fontSize: 12}},
                                     {{ text: " राहणार   ", fontSize: 10 }},
                                     {{ text: (row["village"] || "") + "  ", fontSize: 12}},
                                     {{ text: "     तालुका:  ", fontSize: 10 }},
                                     {{ text: form_data.taluka, fontSize: 12 }},
                                     {{ text: "    जिल्हा:  ", fontSize: 10 }},
                                     {{ text: form_data.jilha, fontSize: 12 }},
                                 ],
                                lineHeight: 0.7, margin: [3, 0, 0, 0]
                                 }},
                            {{ text: "    ", fontSize: 5}},
                            {{ text: "असा अर्ज करतो की,यात पुढे नमूद केलेली व वर्णिलेली जमीन ओलिता खाली आणण्यासाठी मुंबई पाटबंधारे अधिनियम १८७९ व त्या वेळी अमंलात असलेला", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
                            {{ text: "पाटबंधारे विषयक इतर कोणताही अधिनियम यांच्या तरतुदीनुसार व मुंबई कालवे नियम १९३४ च्या तरतुदीनुसार या नमुन्यांच्या मागील पृष्ठावर विशेष नमूद", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
                            {{ text: "केलेल्या व मला मान्य असलेल्या शर्तीना अधीन राहून मला कृपया नदी/धरण पाणी पुरवण्यात यावे :-", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},    
                            {{ text: "    ", fontSize: 4}}, 
                            {{ 
                               absolutePosition: {{ x: 514, y: 350 }},
                                 stack: [
                                    {{ text: form_data.start_date, alignment: 'center' }},
                                    {{ text: 'ते', alignment: 'center' }},
                                    {{ text: form_data.end_date, alignment: 'center' }}
                                   ],
                                   lineHeight: 0.7,
                             }},
                               {{ 
                               absolutePosition: {{ x: -360, y: 350 }},
                                 stack: [
                                    {{ text: jlashypart[0], alignment: 'center' }},
                                    {{ text: jlashypart[1], alignment: 'center' }},
                                    {{ text: jlashypart[2], alignment: 'center' }},
                                    {{ text: jlashypart[3], alignment: 'center' }}
                                   ],
                                   lineHeight: 0.7,
                             }},    
                        ],
                        
     
                      }});
                      
                      
        content.push({{
            table: {{
        headerRows: 2,
        widths: [
               "12%", "12%", "8%", "9%", 
               "6%", "6%", "6%", "6%", 
                "6%", "6%", "10%", "13%"
                ],
        body: [
            // 🔹 First header row
            [
                   {{ text: 'गावाचे नांव', rowSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,50,0,2] }},
                   {{ text: 'पाण्याचे वाटप करणाऱ्या जलाशयाचे नाव', rowSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,25,0,2] }},
                   {{ text: 'सर्वेक्षण क्रमांक', rowSpan: 2, fontSize: 12, bold: true, alignment: 'center', lineHeight: 0.7, margin:[0,50,0,2] }},
                   {{ text: 'पोटहिस्सा क्रमांक', rowSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,50,0,2] }},

                   {{ text: 'सर्वेक्षण क्रमांकाचे/पोटहिस्सा क्रमांकाचे एकूण क्षेत्रफळ', colSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,5,0,2] }}, {{}},
                   {{ text: 'सर्वेक्षण/पोटहिस्सा क्रमांकातील धारण जमिनीचे एकूण क्षेत्रफळ', colSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,5,0,2] }}, {{}},
                   {{ text: 'ज्या क्षेत्राकरिता पाण्याची मागणी केली ते एकूण क्षेत्रफळ', colSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,5,0,2] }}, {{}},

                   {{ text: 'पिकाचे नांव', rowSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,50,0,2] }},
                   {{ text: 'ज्या मुदतीसाठी पाणी पाहिजे ती मुदत', rowSpan: 2, fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,30,0,2] }},
            ],
            // 🔹 Second header row
            [
                {{}}, {{}}, {{}}, {{}},

                 {{ text: 'हेक्टर', fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,2,0,2] }},
                 {{ text: 'आर', fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,2,0,2] }},

                 {{ text: 'हेक्टर', fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,2,0,2] }},
                 {{ text: 'आर', fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,2,0,2] }},

                 {{ text: 'हेक्टर', fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,2,0,2] }},
                 {{ text: 'आर', fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,2,0,2] }},

                 {{}}, {{}}
              ],

            ]    
           }},
           layout: {{
                
                fillColor: function (rowIndex, node, columnIndex) {{return (rowIndex < 2) ? '#f2f2f2' : null;}}
            }},

        }});

                    
    content.push({{
                 table: {{
                 widths: [
                                     "12%", "12%", "8%", "9%", 
                                     "6%", "6%", "6%", "6%", 
                                     "6%", "6%", "10%", "13%"
                                 ],
                 body: [[
               {{ text: row["village"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},

               {{ text: row["no"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: row["pno"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},

               {{ text: row["bsarea_int"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: row["bsarea_frac"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},

               {{ text: row["mkarea_int"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: row["mkarea_frac"], fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
                         
               {{ text: row["pmarea_int"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: row["pmarea_frac"], fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},

               {{ text: row["crop"] || "", fontSize: 11, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: "", fontSize: 9, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,0,0,0],border: [true, false, true, false] }}
             ]]
         }}
      }});    
     }}
    j=40;
    p=0.70;
    var tbody = [];
while (i < rows.length - 1 && !rows[i+1]?.name) {{
    i++;
    j = j*p;
    p = p*0.50;
    row = rows[i];
    
      content.push({{
                 table: {{
                 widths: [
                                     "12%", "12%", "8%", "9%", 
                                     "6%", "6%", "6%", "6%", 
                                     "6%", "6%", "10%", "13%"
                                 ],
                 body: [[
               {{text:"",border: [true, false, true, false]}}, 
               {{text:"",border: [true, false, true, false]}},

               {{ text: row["no"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false]}},
               {{ text: row["pno"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false] }},

               {{ text: row["bsarea_int"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0], border: [true, false, true, false] }},
               {{ text: row["bsarea_frac"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0], border: [true, false, true, false] }},

               {{ text: row["mkarea_int"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: row["mkarea_frac"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false] }},
                         
               {{ text: row["pmarea_int"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false] }},
               {{ text: row["pmarea_frac"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false] }},

               {{ text: row["crop"] || "", fontSize: 11, bold: true, alignment: 'center', margin:[0,0,0,0],border: [true, false, true, false] }},
               {{text:"",border: [true, false, true, false]}}
             ]]
         }}
     }});
}}

content.push({{
                 table: {{
                 widths: [
                                     "12%", "12%", "8%", "9%", 
                                     "6%", "6%", "6%", "6%", 
                                     "6%", "6%", "10%", "13%"
                                 ],
                 body: [[
               {{text:"", margin:[0,j,0,0], border: [true, false, true, true]}}, 
               {{text:"", margin:[0,j,0,0], border: [true, false, true, true]}},

               {{ text: "", margin:[0,j,0,0],border: [true, false, true, true]}},
               {{ text: "", margin:[0,j,0,0],border: [true, false, true, true] }},

               {{ text: "एकूण", fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0], border: [false, false, false, true] }},
               {{ text: "=", fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0], border: [false, false, false, true] }},

               {{ text:row["mkarea_sum_int"], fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0],border: [true, false, true, true] }},
               {{ text: row["mkarea_sum_frac"], fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0],border: [true, false, true, true] }},
                         
               {{ text: row["pmarea_sum_int"], fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0],border: [true, false, true, true] }},
               {{ text: row["pmarea_sum_frac"], fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0],border: [false, false, false, true] }},

               {{ text: "", fontSize: 12, bold: true, alignment: 'center',lineHeight: 0.7, margin:[0,j,0,0],border: [true, false, true, true] }},
               {{text:"", margin:[0,j,0,0], border: [true, false, true, true]}}
             ]]
         }}
    
      }});
    
    content.push({{
      stack: [
         {{ text: " ", fontSize: 20 }},
         {{ text: "मंजुरी शिफारस            (" + form_data.je_name + ")", fontSize: 12,lineHeight: 0.7, margin: [360,0,0,0]}},  
         {{ text: "शाखाधिकारी", fontSize: 10,lineHeight: 0.7, margin: [463,0,0,0]}},
         {{ text: "२. ज्या जमिनीकरिता पाणी मिळावे म्हणून अर्ज केला आहे त्या जमिनीचा मी मालक आहे.                                                                  " + form_data.shakha,lineHeight: 0.7, fontSize: 10}},
         {{ text: "३. २०        च्या          हंगामापर्यंतच्या पाणीपट्टीची अदत्त थकबाकी मी भरलेली आहे.फक्त             च्या पाणीपट्टीची रक्‍कम माझ्याकडून येणे आहे.",lineHeight: 0.8, fontSize: 10}},
         {{ text: "४. ज्या व्यक्‍तीला ह्या अर्जावाबत आदेश द्यावयाचा आहे त्याचे नांव, पत्ता व तो आदेश कळवण्याची पद्धती खालीलप्रमाणे आहेत:-",lineHeight: 0.8, fontSize: 10}},
         {{ text: "तारीख        माहे,        २०      अर्जदाराची सही अगर त्याच्या", fontSize: 10,lineHeight: 0.8, margin: [7, 0, 0, 0]}},
         {{ text: "डाव्या हाताच्या अंगठ्याचा ठसा", fontSize: 10,lineHeight: 0.8, margin: [101, 0, 0, 0]}},
         {{ text: "    ",lineHeight: 0.8, fontSize: 5}},
         {{ text: "साक्षीदाराची सही", fontSize: 10,lineHeight: 0.8, margin: [15, 0, 0, 0]}},
         {{ text: "    ",lineHeight: 0.8, fontSize: 3}},
         {{ text: "ज्या जमिनीच्या बाबतीत अर्जदार जमिनीचा खातेदार नसेल अगर वरिष्ठ धारक नसेल",lineHeight: 0.8, fontSize: 10}},
         {{ text: "अशा जमिनीच्या बाबतीत जमिनीच्या खातेदाराची किंवा सामायिक खातेदारांच्या किंवा",lineHeight: 0.8, fontSize: 10}},
         {{ text: "वरिष्ठ धारकाची किंवा सामायिक वरिष्ठ धारकाची सही किंवा सह्या किंवा डाव्या हाताच्या",lineHeight: 0.8, fontSize: 10}},
         {{ text: "    ",lineHeight: 0.8, fontSize: 5}},
         {{ text: "अंगठ्याचा ठसा किंवा ठसे",lineHeight: 0.8, fontSize: 10, margin: [10, 0, 0, 0]}},
         {{ text: "    ",lineHeight: 0.8, fontSize: 3}},
         {{ text: "खालील नमूद केल्याप्रमाणे मंजुरीकरीता रवाना :- पर्यंत                                            मंजुर",lineHeight: 0.8, fontSize: 10, margin: [3, 0, 0, 0]}},
         {{ text: "१) मंजुर करावयाचे क्षेत्र -      हेक्‍टर       आर       (२)मंजुरीची मुदत-  " + form_data.start_date +  " पासून " +  form_data.end_date + "                                               पर्यंत", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
         {{ text: "३) एकरीआकारावयाच्या पाणीपट्टीचा दर -        रु.", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
         {{ text: "तारीख           माहे           २०", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
         {{ text: "मंजुर                                                                              " + form_data.upofficer + "       उपविभाग", fontSize: 10,lineHeight: 0.8, margin: [150, 0, 0, 0]}},
         {{ text: "तारीख          माहे             २०                                                                                                     " + form_data.upvibhag , fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
         {{ text: "उपविभाग, " + form_data.upoffice, fontSize: 10,lineHeight: 0.8, margin: [378, 0, 0, 0]}},
         {{ text: "टिप : सूचना क्रमांक ७ प्रमाणे मालक नसणाऱ्या अर्जदारानी नेहमीप्रामणे द्यावयाच्या जामीन पत्राचा तपशील", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
         {{ text: "जामीन राहणारांची नावे - (१)                                                             नमुना क्रमांक ८ प्रमाणे", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
         {{ text: "(२)", fontSize: 10,lineHeight: 0.8, margin: [86, 0, 0, 0]}},
         {{ text: "नमुना क्रमांक ९ प्रमाणे तारणादाखल दिलेला चा सर्वेक्षण क्रमांक                                                             कार्यकारी अभियंता                    विभाग", fontSize: 10,lineHeight: 0.8, margin: [3, 0, 0, 0]}},
      ],
      pageBreak: (i < rows.length - 1) ? "after" : ""   // no blank last page
    }}); 
   
      
 }}  //forloop end
                    var docDef = {{
                    pageSize: 'A4',
                    pageMargins: [15, 18, 15,0], 
                    content: content,
                    defaultStyle: {{
                        font: "MarathiFont"
                    }}
                 }};
        // Preview in new tab
            function previewPDF() {{
                pdfMake.createPdf(docDef).open();
            }}

        // Download directly
            function downloadPDF() {{
                pdfMake.createPdf(docDef).download(form_data.village);
                alert("✅ PDF downloaded successfully!");

            }}
     
                               </script>
                               </body>
                               </html>
                               """,
                              height=750,
                              scrolling=True
                         )
