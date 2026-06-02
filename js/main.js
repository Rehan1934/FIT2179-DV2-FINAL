// ============================================================
// FIT2179 DV2 FINAL MAIN SCRIPT
// Malaysia's Mental Health Crisis
// Clean version with robust KPI rendering and ASEAN choropleth.
// ============================================================

const ASEAN_DATA = [
  { country: "Malaysia", id: 458, longitude: 101.9758, latitude: 4.2105, depression: 3.52, anxiety: 4.34, group: "Malaysia" },
  { country: "Singapore", id: 702, longitude: 103.8198, latitude: 1.3521, depression: 3.44, anxiety: 3.73, group: "Other ASEAN countries" },
  { country: "Thailand", id: 764, longitude: 100.9925, latitude: 15.87, depression: 3.09, anxiety: 3.33, group: "Other ASEAN countries" },
  { country: "Cambodia", id: 116, longitude: 104.991, latitude: 12.5657, depression: 3.09, anxiety: 3.29, group: "Other ASEAN countries" },
  { country: "Laos", id: 418, longitude: 102.4955, latitude: 19.8563, depression: 2.91, anxiety: 4.22, group: "Other ASEAN countries" },
  { country: "Vietnam", id: 704, longitude: 108.2772, latitude: 14.0583, depression: 2.88, anxiety: 2.07, group: "Other ASEAN countries" },
  { country: "Philippines", id: 608, longitude: 121.774, latitude: 12.8797, depression: 2.77, anxiety: 3.27, group: "Other ASEAN countries" },
  { country: "Indonesia", id: 360, longitude: 113.9213, latitude: -0.7893, depression: 2.64, anxiety: 3.28, group: "Other ASEAN countries" },
  { country: "Brunei", id: 96, longitude: 114.7277, latitude: 4.5353, depression: 2.56, anxiety: 3.62, group: "Other ASEAN countries" },
  { country: "Myanmar", id: 104, longitude: 95.956, latitude: 21.9162, depression: 2.30, anxiety: 3.31, group: "Other ASEAN countries" }
];

function chartConfig() {
  return {
    background: "transparent",
    font: "Inter",
    view: { stroke: null },
    axis: {
      labelFont: "Inter",
      titleFont: "Inter",
      labelColor: "#52616b",
      titleColor: "#132238",
      gridColor: "#e8eef5",
      domainColor: "#d6e0ea",
      tickColor: "#d6e0ea"
    },
    legend: {
      labelFont: "Inter",
      titleFont: "Inter",
      labelColor: "#52616b",
      titleColor: "#132238",
      orient: "bottom"
    },
    title: {
      font: "Inter",
      fontWeight: 800,
      color: "#132238",
      anchor: "start"
    }
  };
}

// ------------------------------------------------------------
// Robust container finder.
// This fixes cases where the chart ID changed or an old script cleared it.
// ------------------------------------------------------------

function getChartContainer(selector, headingText) {
  const byId = document.querySelector(selector);
  if (byId) return byId;

  const cards = Array.from(document.querySelectorAll(".chart-card"));
  const match = cards.find(card => {
    const heading = card.querySelector("h3");
    return heading && heading.textContent.trim().toLowerCase().includes(headingText.toLowerCase());
  });

  if (!match) return null;

  let chart = match.querySelector(".chart");
  if (!chart) {
    chart = document.createElement("div");
    chart.className = "chart";
    match.insertBefore(chart, match.querySelector(".insight"));
  }

  return chart;
}

// ============================================================
// STUDENT SURVEY SNAPSHOT
// Custom dashboard-style cards.
// This is intentionally not a plain Vega chart because it is a
// high-level summary/annotation component.
// ============================================================

function renderStudentSnapshotCards() {
  const element = getChartContainer("#vis-kpi", "student survey snapshot");
  if (!element) return;

  element.innerHTML = `
    <div style="
      display:grid;
      grid-template-columns:repeat(3, minmax(0, 1fr));
      gap:18px;
      margin:8px 0 4px;
      width:100%;
    ">
      ${kpiCard("Reported any symptom", "63.4%", "64 of 101 students reported at least one symptom.", "Derived symptom burden", "#4f8fc0")}
      ${kpiCard("Reported depression", "34.7%", "35 of 101 students reported depression.", "Symptom indicator", "#7c6bb0")}
      ${kpiCard("Reported anxiety", "33.7%", "34 of 101 students reported anxiety.", "Symptom indicator", "#7c6bb0")}
      ${kpiCard("Reported panic attacks", "32.7%", "33 of 101 students reported panic attacks.", "Symptom indicator", "#e08e79")}
      ${kpiCard("Reported two or more symptoms", "27.7%", "28 of 101 students reported overlapping symptoms.", "Derived overlap indicator", "#e08e79")}
      ${kpiCard("Sought specialist treatment", "5.9%", "Only 6 of 101 students reported specialist treatment-seeking.", "Formal support indicator", "#65a891")}
    </div>
  `;
}

function kpiCard(label, value, meta, chip, color) {
  return `
    <div style="
      border:1px solid #dce7f1;
      border-radius:18px;
      padding:18px;
      background:linear-gradient(135deg, #ffffff 0%, #f4f8fb 100%);
      box-shadow:0 10px 24px rgba(17, 32, 54, 0.06);
      min-height:155px;
    ">
      <div style="
        font-size:0.86rem;
        font-weight:800;
        color:#112036;
        margin-bottom:8px;
      ">${label}</div>

      <div style="
        font-size:2.25rem;
        line-height:1;
        font-weight:800;
        color:${color};
        margin-bottom:9px;
      ">${value}</div>

      <div style="
        font-size:0.84rem;
        color:#586879;
        min-height:42px;
      ">${meta}</div>

      <span style="
        display:inline-block;
        margin-top:12px;
        padding:5px 9px;
        border-radius:999px;
        background:#eef4fb;
        color:#52616b;
        font-size:0.78rem;
        font-weight:700;
      ">${chip}</span>
    </div>
  `;
}

// ============================================================
// ASEAN CHOROPLETH MAP + RANKING
// This is closer to your friend's Australia map.
// If external map boundaries fail, the script falls back to coordinate map.
// ============================================================

function aseanChoroplethSpec() {
  const rankingValues = [
    { country: "Malaysia", depression: 3.52, anxiety: 4.34, group: "Malaysia" },
    { country: "Singapore", depression: 3.44, anxiety: 3.73, group: "Other ASEAN countries" },
    { country: "Thailand", depression: 3.09, anxiety: 3.33, group: "Other ASEAN countries" },
    { country: "Cambodia", depression: 3.09, anxiety: 3.29, group: "Other ASEAN countries" },
    { country: "Laos", depression: 2.91, anxiety: 4.22, group: "Other ASEAN countries" },
    { country: "Vietnam", depression: 2.88, anxiety: 2.07, group: "Other ASEAN countries" },
    { country: "Philippines", depression: 2.77, anxiety: 3.27, group: "Other ASEAN countries" },
    { country: "Indonesia", depression: 2.64, anxiety: 3.28, group: "Other ASEAN countries" },
    { country: "Brunei", depression: 2.56, anxiety: 3.62, group: "Other ASEAN countries" },
    { country: "Myanmar", depression: 2.30, anxiety: 3.31, group: "Other ASEAN countries" }
  ];

  const hoverPoints = [
    { country: "Myanmar", longitude: 96.5, latitude: 20.5, depression: 2.30, anxiety: 3.31 },
    { country: "Thailand", longitude: 100.8, latitude: 15.4, depression: 3.09, anxiety: 3.33 },
    { country: "Laos", longitude: 103.8, latitude: 18.5, depression: 2.91, anxiety: 4.22 },
    { country: "Cambodia", longitude: 104.8, latitude: 12.2, depression: 3.09, anxiety: 3.29 },
    { country: "Vietnam", longitude: 108.7, latitude: 15.6, depression: 2.88, anxiety: 2.07 },
    { country: "Philippines", longitude: 122.1, latitude: 13.0, depression: 2.77, anxiety: 3.27 },
    { country: "Malaysia", longitude: 102.4, latitude: 4.2, depression: 3.52, anxiety: 4.34 },
    { country: "Singapore", longitude: 103.9, latitude: 1.3, depression: 3.44, anxiety: 3.73 },
    { country: "Brunei", longitude: 114.8, latitude: 4.8, depression: 2.56, anxiety: 3.62 },
    { country: "Indonesia", longitude: 113.5, latitude: -3.8, depression: 2.64, anxiety: 3.28 }
  ];

  return {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Large ASEAN choropleth map and ranking chart. Country polygons encode estimated depression prevalence, Malaysia is outlined, and hover points provide correct country tooltips.",
    "hconcat": [
      {
        "title": {
          "text": "ASEAN choropleth map",
          "subtitle": "Darker shading indicates higher estimated depression prevalence. Malaysia is outlined.",
          "fontSize": 16,
          "subtitleFontSize": 11,
          "subtitleColor": "#52616b",
          "anchor": "start"
        },
        "width": 740,
        "height": 580,
        "projection": {
          "type": "mercator",
          "center": [116, 10],
          "scale": 680,
          "translate": [370, 290]
        },
        "layer": [
          {
            "data": {
              "url": "data/processed/asean_map_final.geojson",
              "format": {
                "type": "json",
                "property": "features"
              }
            },
            "transform": [
              { "calculate": "datum.properties.country", "as": "country" },
              { "calculate": "datum.properties.depression", "as": "depression" },
              { "calculate": "datum.properties.anxiety", "as": "anxiety" }
            ],
            "mark": {
              "type": "geoshape",
              "stroke": "#ffffff",
              "strokeWidth": 1.15
            },
            "encoding": {
              "color": {
                "field": "depression",
                "type": "quantitative",
                "title": "Depression (%)",
                "scale": {
                  "scheme": "oranges",
                  "domain": [2.2, 3.6]
                }
              }
            }
          },
          {
            "data": {
              "url": "data/processed/asean_map_final.geojson",
              "format": {
                "type": "json",
                "property": "features"
              }
            },
            "transform": [
              { "filter": "datum.properties.country === 'Malaysia'" }
            ],
            "mark": {
              "type": "geoshape",
              "fillOpacity": 0,
              "stroke": "#112036",
              "strokeWidth": 4
            }
          },
          {
            "data": {
              "values": hoverPoints
            },
            "mark": {
              "type": "circle",
              "size": 160,
              "opacity": 0.001
            },
            "encoding": {
              "longitude": {
                "field": "longitude",
                "type": "quantitative"
              },
              "latitude": {
                "field": "latitude",
                "type": "quantitative"
              },
              "tooltip": [
                {
                  "field": "country",
                  "type": "nominal",
                  "title": "Country"
                },
                {
                  "field": "depression",
                  "type": "quantitative",
                  "title": "Depression (%)",
                  "format": ".2f"
                },
                {
                  "field": "anxiety",
                  "type": "quantitative",
                  "title": "Anxiety (%)",
                  "format": ".2f"
                }
              ]
            }
          },
          {
            "data": {
              "values": [
                { country: "Malaysia", longitude: 102.4, latitude: 4.2 }
              ]
            },
            "mark": {
              "type": "text",
              "fontSize": 14,
              "fontWeight": 900,
              "color": "#112036",
              "dx": 34,
              "dy": -12
            },
            "encoding": {
              "longitude": {
                "field": "longitude",
                "type": "quantitative"
              },
              "latitude": {
                "field": "latitude",
                "type": "quantitative"
              },
              "text": {
                "field": "country",
                "type": "nominal"
              }
            }
          }
        ]
      },
      {
        "title": {
          "text": "Latest ASEAN ranking",
          "subtitle": "Estimated depression prevalence, 2017.",
          "fontSize": 16,
          "subtitleFontSize": 11,
          "subtitleColor": "#52616b",
          "anchor": "start"
        },
        "data": {
          "values": rankingValues
        },
        "width": 330,
        "height": 470,
        "layer": [
          {
            "mark": {
              "type": "bar",
              "cornerRadiusEnd": 6
            },
            "encoding": {
              "y": {
                "field": "country",
                "type": "nominal",
                "sort": "-x",
                "title": null
              },
              "x": {
                "field": "depression",
                "type": "quantitative",
                "title": "Depression (%)",
                "scale": {
                  "domain": [0, 4]
                }
              },
              "color": {
                "field": "group",
                "type": "nominal",
                "legend": null,
                "scale": {
                  "domain": ["Malaysia", "Other ASEAN countries"],
                  "range": ["#bf4b00", "#f28e2b"]
                }
              },
              "tooltip": [
                {
                  "field": "country",
                  "type": "nominal",
                  "title": "Country"
                },
                {
                  "field": "depression",
                  "type": "quantitative",
                  "title": "Depression (%)",
                  "format": ".2f"
                },
                {
                  "field": "anxiety",
                  "type": "quantitative",
                  "title": "Anxiety (%)",
                  "format": ".2f"
                }
              ]
            }
          },
          {
            "mark": {
              "type": "text",
              "align": "left",
              "dx": 6,
              "fontWeight": 800,
              "color": "#132238"
            },
            "encoding": {
              "y": {
                "field": "country",
                "type": "nominal",
                "sort": "-x"
              },
              "x": {
                "field": "depression",
                "type": "quantitative"
              },
              "text": {
                "field": "depression",
                "type": "quantitative",
                "format": ".2f"
              }
            }
          }
        ]
      }
    ],
    "spacing": 25,
    "resolve": {
      "scale": {
        "color": "independent"
      }
    },
    "config": chartConfig()
  };
}

function aseanCoordinateFallbackSpec() {
  return {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Fallback ASEAN coordinate map and ranking chart.",
    "hconcat": [
      {
        "title": {
          "text": "ASEAN coordinate map",
          "subtitle": "Position uses longitude and latitude; bubble size and colour encode estimated depression prevalence.",
          "fontSize": 16,
          "subtitleFontSize": 11,
          "subtitleColor": "#52616b",
          "anchor": "start"
        },
        "data": { "values": ASEAN_DATA },
        "width": 520,
        "height": 370,
        "layer": [
          {
            "mark": {
              "type": "circle",
              "opacity": 0.88,
              "stroke": "#ffffff",
              "strokeWidth": 1.6
            },
            "encoding": {
              "x": {
                "field": "longitude",
                "type": "quantitative",
                "title": "Longitude",
                "scale": { "domain": [92, 126] }
              },
              "y": {
                "field": "latitude",
                "type": "quantitative",
                "title": "Latitude",
                "scale": { "domain": [-5, 24] }
              },
              "size": {
                "field": "depression",
                "type": "quantitative",
                "title": "Depression (%)",
                "scale": { "range": [180, 1500] }
              },
              "color": {
                "field": "depression",
                "type": "quantitative",
                "title": "Depression (%)",
                "scale": {
                  "scheme": "purples",
                  "domain": [2.2, 3.6]
                }
              },
              "tooltip": [
                { "field": "country", "type": "nominal", "title": "Country" },
                { "field": "depression", "type": "quantitative", "title": "Depression (%)", "format": ".2f" },
                { "field": "anxiety", "type": "quantitative", "title": "Anxiety (%)", "format": ".2f" }
              ]
            }
          },
          {
            "transform": [{ "filter": "datum.country === 'Malaysia'" }],
            "mark": {
              "type": "circle",
              "fillOpacity": 0,
              "stroke": "#e08e79",
              "strokeWidth": 4,
              "size": 2100
            },
            "encoding": {
              "x": { "field": "longitude", "type": "quantitative", "scale": { "domain": [92, 126] } },
              "y": { "field": "latitude", "type": "quantitative", "scale": { "domain": [-5, 24] } }
            }
          },
          {
            "mark": {
              "type": "text",
              "align": "left",
              "dx": 9,
              "dy": -9,
              "fontSize": 10,
              "fontWeight": 700,
              "color": "#52616b"
            },
            "encoding": {
              "x": { "field": "longitude", "type": "quantitative", "scale": { "domain": [92, 126] } },
              "y": { "field": "latitude", "type": "quantitative", "scale": { "domain": [-5, 24] } },
              "text": { "field": "country" }
            }
          }
        ]
      },
      {
        "title": {
          "text": "Latest ASEAN ranking",
          "subtitle": "Estimated depression prevalence, 2017.",
          "fontSize": 16,
          "subtitleFontSize": 11,
          "subtitleColor": "#52616b",
          "anchor": "start"
        },
        "data": { "values": ASEAN_DATA },
        "width": 300,
        "height": 370,
        "layer": [
          {
            "mark": { "type": "bar", "cornerRadiusEnd": 6 },
            "encoding": {
              "y": { "field": "country", "type": "nominal", "sort": "-x", "title": null },
              "x": { "field": "depression", "type": "quantitative", "title": "Depression (%)", "scale": { "domain": [0, 4] } },
              "color": {
                "field": "group",
                "type": "nominal",
                "legend": null,
                "scale": {
                  "domain": ["Malaysia", "Other ASEAN countries"],
                  "range": ["#e08e79", "#7c6bb0"]
                }
              }
            }
          },
          {
            "mark": { "type": "text", "align": "left", "dx": 6, "fontWeight": 800, "color": "#132238" },
            "encoding": {
              "y": { "field": "country", "type": "nominal", "sort": "-x" },
              "x": { "field": "depression", "type": "quantitative" },
              "text": { "field": "depression", "type": "quantitative", "format": ".2f" }
            }
          }
        ]
      }
    ],
    "resolve": { "scale": { "color": "independent", "size": "independent" } },
    "config": chartConfig()
  };
}

// ============================================================
// Other guaranteed inline charts
// ============================================================

function treatmentGapSpec() {
  return {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": { "url": "data/processed/treatment_gap.csv" },
    "width": 900,
    "height": 280,
    "transform": [
      {
        "calculate": "datum.type == 'Gap' ? 'Unmet support gap' : datum.type == 'Support' ? 'Formal help-seeking' : 'Reported distress'",
        "as": "derived_message"
      }
    ],
    "layer": [
      {
        "mark": { "type": "bar", "cornerRadiusEnd": 10, "opacity": 0.9 },
        "encoding": {
          "y": {
            "field": "category",
            "type": "nominal",
            "sort": [
              "Reported at least one symptom",
              "Symptomatic but no specialist treatment",
              "Sought specialist treatment"
            ],
            "title": null,
            "axis": { "labelLimit": 260 }
          },
          "x": {
            "field": "percentage",
            "type": "quantitative",
            "title": "Student respondents (%)",
            "scale": { "domain": [0, 70] }
          },
          "color": {
            "field": "type",
            "type": "nominal",
            "title": "Indicator type",
            "scale": {
              "domain": ["Symptom", "Gap", "Support"],
              "range": ["#4f8fc0", "#e08e79", "#65a891"]
            }
          },
          "tooltip": [
            { "field": "category", "type": "nominal", "title": "Category" },
            { "field": "derived_message", "type": "nominal", "title": "Interpretation" },
            { "field": "percentage", "type": "quantitative", "title": "Respondents (%)", "format": ".1f" },
            { "field": "count", "type": "quantitative", "title": "Count" },
            { "field": "total", "type": "quantitative", "title": "Total" }
          ]
        }
      },
      {
        "mark": { "type": "point", "filled": true, "size": 100, "stroke": "#ffffff", "strokeWidth": 1.3 },
        "encoding": {
          "y": {
            "field": "category",
            "type": "nominal",
            "sort": [
              "Reported at least one symptom",
              "Symptomatic but no specialist treatment",
              "Sought specialist treatment"
            ]
          },
          "x": { "field": "percentage", "type": "quantitative" },
          "color": {
            "field": "type",
            "type": "nominal",
            "legend": null,
            "scale": {
              "domain": ["Symptom", "Gap", "Support"],
              "range": ["#4f8fc0", "#e08e79", "#65a891"]
            }
          }
        }
      },
      {
        "mark": { "type": "text", "align": "left", "dx": 9, "fontWeight": 800, "color": "#132238" },
        "encoding": {
          "y": {
            "field": "category",
            "type": "nominal",
            "sort": [
              "Reported at least one symptom",
              "Symptomatic but no specialist treatment",
              "Sought specialist treatment"
            ]
          },
          "x": { "field": "percentage", "type": "quantitative" },
          "text": { "field": "percentage", "type": "quantitative", "format": ".1f" }
        }
      }
    ],
    "config": chartConfig()
  };
}

function cgpaSpec() {
  return {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": { "url": "data/processed/cgpa_symptoms.csv" },
    "width": 900,
    "height": 310,
    "transform": [
      {
        "calculate": "datum.percentage >= 60 ? 'High symptom-share group' : datum.percentage >= 40 ? 'Medium symptom-share group' : 'Lower symptom-share group'",
        "as": "derived_band"
      }
    ],
    "layer": [
      {
        "mark": { "type": "bar", "cornerRadiusEnd": 10, "opacity": 0.9 },
        "encoding": {
          "y": {
            "field": "cgpa",
            "type": "ordinal",
            "sort": ["0 - 1.99", "2.00 - 2.49", "2.50 - 2.99", "3.00 - 3.49", "3.50 - 4.00"],
            "title": "CGPA range"
          },
          "x": {
            "field": "percentage",
            "type": "quantitative",
            "title": "Students with at least one reported symptom (%)",
            "scale": { "domain": [0, 100] }
          },
          "color": {
            "field": "derived_band",
            "type": "nominal",
            "title": "Derived symptom-share band",
            "scale": {
              "domain": ["Lower symptom-share group", "Medium symptom-share group", "High symptom-share group"],
              "range": ["#b7c4d0", "#7c6bb0", "#e08e79"]
            }
          },
          "tooltip": [
            { "field": "cgpa", "type": "nominal", "title": "CGPA range" },
            { "field": "derived_band", "type": "nominal", "title": "Derived band" },
            { "field": "percentage", "type": "quantitative", "title": "Students (%)", "format": ".1f" },
            { "field": "count", "type": "quantitative", "title": "Count" },
            { "field": "total", "type": "quantitative", "title": "Total" }
          ]
        }
      },
      {
        "mark": { "type": "point", "filled": true, "size": 95, "stroke": "#ffffff", "strokeWidth": 1.3 },
        "encoding": {
          "y": {
            "field": "cgpa",
            "type": "ordinal",
            "sort": ["0 - 1.99", "2.00 - 2.49", "2.50 - 2.99", "3.00 - 3.49", "3.50 - 4.00"]
          },
          "x": { "field": "percentage", "type": "quantitative" },
          "color": {
            "field": "derived_band",
            "type": "nominal",
            "legend": null,
            "scale": {
              "domain": ["Lower symptom-share group", "Medium symptom-share group", "High symptom-share group"],
              "range": ["#b7c4d0", "#7c6bb0", "#e08e79"]
            }
          }
        }
      },
      {
        "mark": { "type": "text", "align": "left", "dx": 9, "fontWeight": 800, "color": "#132238" },
        "encoding": {
          "y": {
            "field": "cgpa",
            "type": "ordinal",
            "sort": ["0 - 1.99", "2.00 - 2.49", "2.50 - 2.99", "3.00 - 3.49", "3.50 - 4.00"]
          },
          "x": { "field": "percentage", "type": "quantitative" },
          "text": { "field": "percentage", "type": "quantitative", "format": ".1f" }
        }
      }
    ],
    "config": chartConfig()
  };
}

function pressureProfileSpec() {
  return {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": { "url": "data/processed/pressure_profile.csv" },
    "width": 900,
    "height": 430,
    "transform": [
      {
        "calculate": "isValid(datum.evidence_layer) ? datum.evidence_layer : datum.domain",
        "as": "layer_name"
      },
      {
        "calculate": "datum.percentage >= 50 ? 'Very visible' : datum.percentage >= 20 ? 'Moderate warning' : 'Low but important'",
        "as": "derived_intensity"
      }
    ],
    "layer": [
      {
        "mark": { "type": "bar", "cornerRadiusEnd": 10, "opacity": 0.88 },
        "encoding": {
          "y": {
            "field": "indicator",
            "type": "nominal",
            "sort": "-x",
            "title": null,
            "axis": { "labelLimit": 300 }
          },
          "x": {
            "field": "percentage",
            "type": "quantitative",
            "title": "Indicator value (%)",
            "scale": { "domain": [0, 100] }
          },
          "color": {
            "field": "layer_name",
            "type": "nominal",
            "title": "Evidence layer",
            "scale": { "range": ["#4f8fc0", "#e08e79", "#7c6bb0", "#65a891"] }
          },
          "tooltip": [
            { "field": "layer_name", "type": "nominal", "title": "Evidence layer" },
            { "field": "indicator", "type": "nominal", "title": "Indicator" },
            { "field": "derived_intensity", "type": "nominal", "title": "Derived intensity" },
            { "field": "percentage", "type": "quantitative", "title": "Value (%)", "format": ".1f" },
            { "field": "interpretation", "type": "nominal", "title": "Interpretation" }
          ]
        }
      },
      {
        "mark": { "type": "point", "filled": true, "size": 95, "stroke": "#ffffff", "strokeWidth": 1.3 },
        "encoding": {
          "y": { "field": "indicator", "type": "nominal", "sort": "-x" },
          "x": { "field": "percentage", "type": "quantitative" },
          "color": {
            "field": "layer_name",
            "type": "nominal",
            "legend": null,
            "scale": { "range": ["#4f8fc0", "#e08e79", "#7c6bb0", "#65a891"] }
          }
        }
      },
      {
        "mark": { "type": "text", "align": "left", "dx": 9, "fontWeight": 800, "color": "#132238" },
        "encoding": {
          "y": { "field": "indicator", "type": "nominal", "sort": "-x" },
          "x": { "field": "percentage", "type": "quantitative" },
          "text": { "field": "percentage", "type": "quantitative", "format": ".1f" }
        }
      }
    ],
    "config": chartConfig()
  };
}

// ============================================================
// Render all charts once
// ============================================================

const externalCharts = [
  ["#vis-trend", "specs/08_malaysia_trend.json"],
  ["#vis-ranking", "specs/09_asean_ranking.json"],
  ["#vis-profile", "specs/11_disorder_profile.json"],
  ["#vis-adolescent", "specs/12_adolescent_profile.json"],
  ["#vis-suicide", "specs/13_attempted_suicide.json"],
  ["#vis-symptoms", "specs/02_symptom_rates.json"],
  ["#vis-overlap", "specs/03_overlap_strip.json"],
  ["#vis-gender", "specs/05_gender_heatmap.json"],
  ["#vis-year", "specs/06_year_heatmap.json"]
];

const inlineCharts = [
  ["#vis-gap", treatmentGapSpec()],
  ["#vis-cgpa", cgpaSpec()],
  ["#vis-pressure", pressureProfileSpec()]
];

async function embedTo(selector, specOrUrl) {
  const element = document.querySelector(selector);
  if (!element) return;

  element.innerHTML = "";

  try {
    await vegaEmbed(selector, specOrUrl, {
      actions: false,
      renderer: "svg"
    });
  } catch (error) {
    console.error(`Failed to load chart for ${selector}`, error);
    element.innerHTML = `
      <p class="chart-error">
        Chart failed to load for ${selector}. Error: ${error.message}
      </p>
    `;
  }
}

async function renderMap() {
  const element = document.querySelector("#vis-map");
  if (!element) return;

  element.innerHTML = "";

  try {
    await vegaEmbed("#vis-map", aseanChoroplethSpec(), {
      actions: false,
      renderer: "svg"
    });
  } catch (error) {
    console.warn("Choropleth failed, using coordinate fallback.", error);
    element.innerHTML = "";
    await vegaEmbed("#vis-map", aseanCoordinateFallbackSpec(), {
      actions: false,
      renderer: "svg"
    });
  }
}

function runDashboard() {
  renderStudentSnapshotCards();
  renderMap();

  externalCharts.forEach(([selector, url]) => {
    embedTo(selector, `${url}?v=${Date.now()}`);
  });

  inlineCharts.forEach(([selector, spec]) => {
    embedTo(selector, spec);
  });

  // Extra safety: render KPI cards again after other async charts start.
  setTimeout(renderStudentSnapshotCards, 500);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", runDashboard);
} else {
  runDashboard();
}