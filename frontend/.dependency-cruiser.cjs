// Architektur-Fitness-Functions für die Vue-SPA (siehe docs/architecture/).
// Ausführen: npm run lint:arch
/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'domain-ist-rein',
      comment: 'domain/ enthält reine TS-Funktionen und importiert nichts außerhalb von domain/.',
      severity: 'error',
      from: { path: '^src/domain/', pathNot: '\\.spec\\.ts$' },
      to: { pathNot: ['^src/domain/', '^node_modules/'] },
    },
    {
      name: 'komponenten-sprechen-nicht-mit-dem-backend',
      comment: 'Nur Views dürfen den API-Client nutzen; Komponenten erhalten Daten über Props/Events.',
      severity: 'error',
      from: { path: '^src/components/', pathNot: '\\.spec\\.ts$' },
      to: { path: '^src/api/client\\.ts$' },
    },
    {
      name: 'komponenten-kennen-keine-views-oder-store',
      severity: 'error',
      from: { path: '^src/components/', pathNot: '\\.spec\\.ts$' },
      to: { path: ['^src/views/', '^src/stores/'] },
    },
    {
      name: 'keine-zirkulaeren-abhaengigkeiten',
      severity: 'error',
      from: {},
      to: { circular: true },
    },
  ],
  options: {
    tsConfig: { fileName: 'tsconfig.app.json' },
    doNotFollow: { path: 'node_modules' },
    exclude: { path: '\\.spec\\.ts$' },
    tsPreCompilationDeps: true,
  },
};
