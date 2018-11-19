# Parser for collinsdictionary.com

## - Spanish - English

### Calls 

#### Get single lang's concise explains/translations
```python
from parser import SpanishEnglish,TransLang
p = SpanishEnglish('ahora')
p.get_langs_trans('.+English'),
p.get_langs_trans(lang=TransLang.Chinese)
```

#### Result
```json
["now", "现在"]
```


#### Get all dictionary-formated 
```python
from parser import SpanishEnglish

print(SpanishEnglish('encantada').to_dict)

```

#### Result:
```json
{
 "frequency": {
  "title": "Extremely Common. día is one of the 1000 most commonly used words in the Collins dictionary",
  "rank": 1000,
  "score": 5
 },
 "translations": {
  "British English": [
   "day",
   "daytime"
  ],
  "American English": [
   "day",
   "daytime"
  ],
  "Arabic": [
   "يَوْم",
   "نَهَار"
  ],
  "Brazilian Portuguese": [
   "dia"
  ],
  "Chinese": [
   "白天",
   "日间"
  ],
  "Croatian": [
   "dan"
  ],
  "Czech": [
   "den"
  ],
  "Danish": [
   "dagtimer",
   "dag"
  ],
  "Dutch": [
   "overdag",
   "dag"
  ],
  "European Spanish": [
   "día"
  ],
  "Finnish": [
   "päiväsaika",
   "päivä"
  ],
  "French": [
   "jour",
   "journée"
  ],
  "German": [
   "Tag"
  ],
  "Greek": [
   "ημέρα"
  ],
  "Italian": [
   "giorno"
  ],
  "Japanese": [
   "昼間",
   "日",
   "一日"
  ],
  "Korean": [
   "주간",
   "낮",
   "하루"
  ],
  "Norwegian": [
   "dag",
   "dagtid"
  ],
  "Polish": [
   "dzień"
  ],
  "European Portuguese": [
   "dia"
  ],
  "Romanian": [
   "zi"
  ],
  "Russian": [
   "сутки",
   "светлое время суток",
   "световой день"
  ],
  "Spanish": [
   "día"
  ],
  "Swedish": [
   "dag"
  ],
  "Thai": [
   "กลางวัน",
   "วัน",
   "เวลากลางวัน"
  ],
  "Turkish": [
   "gündüz",
   "gün"
  ],
  "Ukrainian": [
   "денний час",
   "день"
  ],
  "Vietnamese": [
   "ngày",
   "ban ngày"
  ]
 },
 "entry_title": "English translation of 'día'",
 "orth": "día",
 "url": {
  "audio": "https://www.collinsdictionary.com/sounds/e/es_/es_41/es_419_w0022690.mp3"
 },
 "audio": {
  "name": "dia.mp3"
 },
 "defs": [
  {
   "verb_table_url": null,
   "pos": "masculine noun",
   "explains": [
    {
     "colloc": "",
     "geo": "",
     "register": "",
     "misc": "",
     "syn": "",
     "subj": "",
     "trans": "day",
     "examples": [
      {
       "sentence": "pasaré un par de días en la playa",
       "trans": "I’ll spend a couple of days at the beach"
      },
      {
       "sentence": "todos los días",
       "trans": "every day"
      },
      {
       "sentence": "pollitos de un día",
       "trans": "day-old chicks"
      },
      {
       "sentence": "a los pocos días",
       "trans": "within or after a few days"
      },
      {
       "sentence": "prefiero el día a día",
       "trans": "I prefer to do things from one day to the next or on a day-to-day basis"
      },
      {
       "sentence": "el día a día en la gestión financiera de la empresa",
       "trans": "the day-to-day running of the company’s financial business"
      },
      {
       "sentence": "tres horas al día",
       "trans": "three hours a day"
      },
      {
       "sentence": "al otro día",
       "trans": "the following day"
      },
      {
       "sentence": "al día siguiente",
       "trans": "the following day"
      },
      {
       "sentence": "menú del día",
       "trans": "today’s menu"
      },
      {
       "sentence": "pan del día",
       "trans": "fresh bread"
      }
     ]
    },
    {
     "colloc": "",
     "geo": "",
     "register": "",
     "misc": "",
     "syn": "",
     "subj": "",
     "trans": "daytime",
     "examples": [
      {
       "sentence": "durante el día",
       "trans": "during the day(time)"
      },
      {
       "sentence": "en pleno día",
       "trans": "in broad daylight"
      },
      {
       "sentence": "hace buen día",
       "trans": "the weather’s good today"
      },
      {
       "sentence": "dar los buenos días a algn",
       "trans": "to say good morning to sb"
      },
      {
       "sentence": "duerme de día y trabaja de noche",
       "trans": "he sleeps by day and works by night"
      },
      {
       "sentence": "ya es de día",
       "trans": "it’s already light"
      },
      {
       "sentence": "mientras sea de día",
       "trans": "while it’s still light"
      }
     ]
    },
    {
     "colloc": "",
     "geo": "",
     "register": "",
     "misc": "(del mes)",
     "syn": "",
     "subj": "",
     "trans": "date",
     "examples": [
      {
       "sentence": "¿qué día es hoy?",
       "trans": "what’s the date today?"
      },
      {
       "sentence": "iré pronto, pero no puedo precisar el día",
       "trans": "I’ll be going soon, but I can’t give an exact date"
      },
      {
       "sentence": "llegará el día dos de mayo",
       "trans": "he’ll arrive on the second of May"
      },
      {
       "sentence": "hoy, día cinco de agosto",
       "trans": "today, fifth August"
      },
      {
       "sentence": "día lunes/martes etc",
       "trans": "Monday/Tuesday etc"
      }
     ]
    },
    {
     "colloc": "",
     "geo": "",
     "register": "",
     "misc": "(referido al futuro)",
     "syn": "",
     "subj": "",
     "trans": "",
     "examples": [
      {
       "sentence": "algún día",
       "trans": "some day"
      },
      {
       "sentence": "un buen día",
       "trans": "one fine day"
      },
      {
       "sentence": "cada día es peor",
       "trans": "it’s getting worse every day or by the day"
      },
      {
       "sentence": "un día de estos",
       "trans": "one of these days"
      },
      {
       "sentence": "el día menos pensado",
       "trans": "when you least expect it"
      },
      {
       "sentence": "en los días de la reina Victoria",
       "trans": "in Queen Victoria’s day"
      },
      {
       "sentence": "cualquier día tendrá un accidente",
       "trans": "he’s going to have an accident one of these days or any day now"
      },
      {
       "sentence": "¡cualquier día!",
       "trans": "not on your life!"
      },
      {
       "sentence": "cualquier día viene",
       "trans": "we’ll be waiting till the cows come home for him to turn up"
      },
      {
       "sentence": "¡cualquier día te voy a comprar una casa!",
       "trans": "if you think I’m going to buy you a house you’ve got another think coming!"
      },
      {
       "sentence": "la prensa de nuestros días",
       "trans": "today’s press"
      },
      {
       "sentence": "uno de los principales problemas de nuestros días",
       "trans": "one of the major problems of our day or our times"
      },
      {
       "sentence": "ha durado hasta nuestros días",
       "trans": "it has lasted to the present day"
      },
      {
       "sentence": "dejémoslo para otro día",
       "trans": "let’s leave it for the moment or for another day"
      },
      {
       "sentence": "¡hasta otro día!",
       "trans": "so long!"
      }
     ]
    },
    {
     "colloc": "[estilo]",
     "geo": "",
     "register": "",
     "misc": "",
     "syn": "",
     "subj": "",
     "trans": "",
     "examples": [
      {
       "sentence": "pescado del día",
       "trans": "fresh fish"
      },
      {
       "sentence": "quien quiera estar al día en esta especialidad, que lea ...",
       "trans": "anyone who wishes to keep up to date with this area of study, should read ..."
      },
      {
       "sentence": "está al día vestir así",
       "trans": "it’s the thing to dress like that"
      }
     ]
    }
   ]
  }
 ]
}
```