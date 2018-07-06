

## Get Started

### Errors

- OSError: dlopen() failed to load a library: cairo / cairo-2 / cairo-gobject-2
in windows please install http://www.msys2.org/

You should install https://cairographics.org/download/ first

## Output

### about result.json

Structure:
```json
{
  "segments": [
    {
      "records": {
        "links": [
          {
            "href": "https://policies.yahoo.com/us/en/yahoo/privacy/index.htm"
          }
        ],
        "images": [
          {
            "src": "https://s.yimg.com/cv/api/default/20180321/WORLDCUP_MOBILE_UK_ENG.png",
            "alt": ""
          }
        ],
        "cssselectors": [
          "html > body:nth-child(2) > div:nth-child(7) > div > div:nth-child(4) > div > div:nth-child(6) > div > div > div > form:nth-child(2) > select:nth-child(2) > option"
        ],
        "recordid": 7,
        "texts": [
          "test1"
        ]
      }
    }
  ]
}
```

## Cite
If you use WebSegment in your work please cite our paper!
```text
@article{websegment1,
  title={Event.Locky: System of Event-Data Extraction from Webpages based on Web Mining},
  author={Liao, Chenyi and Hiroi, Kei and Kaji, Katsuhiko and Sakurada, Ken and Kawaguchi, Nobuo},
  journal={Journal of Information Processing},
  volume={25},
  pages = {321--330},
  year={2017}
}
or

@article{websegment2,
  title={An event data extraction method based on HTML structure analysis and machine learning},
  author={Liao, Chenyi and Hiroi, Kei and Kaji, Katsuhiko and Kawaguchi, Nobuo},
  journal={Computer Software and Applications Conference (COMPSAC)},
  volume={3},
  pages = {217-222},
  year={2015}
}

```