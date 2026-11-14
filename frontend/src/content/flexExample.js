// The Home page example: one real PSI record laid against an example scenario.
//
// FLEX values were computed on 14 November 2026 from
// datasets/PSI-69_Experimental table_FLEX.csv (274 rows, 15 columns; the file is cp1252-encoded):
//   oxygen   "O initial ambient composition; mole fraction": 0.12 to 0.34, all 274 rows
//   pressure "Ambient pressure; mmHg": 526.3 to 2,319.9 over 273 rows; one row (C11M201, 6 Sep 2010)
//            records 0 and is left out of the range rather than read as a vacuum
//   fuel     "Fuel": Methanol (157 runs), Heptane (117 runs), burned as droplets
//            ("Droplet initial diameter; mm")
//   air flow the table has no air-flow column
// Gravity comes from the PSI record (flightProgram: International Space Station).
// Replace with the ranking API (#7) once it explains results per condition.
//
// The scenario values are an example a visitor might enter (sea-level air in a spacecraft
// cabin), not NASA data.

export const FLEX_EXAMPLE = {
  accession: 'PSI-69',
  acronym: 'FLEX',
  runs: 274,
  doi: '10.60555/mbq8-0451',
  file: 'PSI-69_Experimental table_FLEX.csv',
  retrieved: '14 Nov 2026',
  lanes: [
    {
      id: 'gravity',
      label: 'Gravity',
      unit: 'level',
      kind: 'stops',
      stops: ['Earth 1 g', 'Mars 0.38 g', 'Moon 0.17 g', 'Micro­gravity'],
      band: 3,
      value: 3,
      status: 'match',
      readout: 'Both in microgravity',
      source: 'the PSI record of PSI-69, flight program International Space Station (ISS).',
    },
    {
      id: 'oxygen',
      label: 'Oxygen',
      unit: 'mole fraction',
      kind: 'range',
      axis: { min: 0.1, max: 0.4, ticks: [0.1, 0.2, 0.3, 0.4] },
      band: [0.12, 0.34],
      value: 0.21,
      status: 'match',
      statusLabel: 'In range',
      readout: '0.12 to 0.34; yours 0.21',
      source: 'column “O initial ambient composition; mole fraction”, all 274 runs.',
    },
    {
      id: 'pressure',
      label: 'Pressure',
      unit: 'mmHg',
      kind: 'range',
      axis: { min: 0, max: 2400, ticks: [0, 600, 1200, 1800, 2400] },
      band: [526.3, 2319.9],
      value: 760,
      status: 'match',
      statusLabel: 'In range',
      readout: '526.3 to 2,319.9; yours 760',
      source: 'column “Ambient pressure; mmHg”, 273 of 274 runs; one run records 0 and is left out.',
    },
    {
      id: 'fuel',
      label: 'Fuel',
      unit: 'phase, material',
      kind: 'pair',
      theirs: 'Liquid droplets: methanol, heptane',
      yours: 'Solid: PMMA',
      status: 'differs',
      readout: 'FLEX liquid, yours solid',
      source: 'column “Fuel”: methanol in 157 runs, heptane in 117, each burned as a droplet.',
    },
    {
      id: 'flow',
      label: 'Air flow',
      unit: 'm/s',
      kind: 'range',
      axis: { min: 0, max: 0.5, ticks: [0, 0.25, 0.5] },
      band: null,
      missingNote: "Not in FLEX's table",
      value: 0.2,
      status: 'missing',
      readout: 'Yours 0.2; FLEX none',
      source: 'none of the 15 columns in the FLEX table records air flow.',
    },
  ],
}
