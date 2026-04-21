declare module 'cytoscape-dagre' {
  const dagre: (cytoscape: typeof import('cytoscape')) => void;
  export default dagre;
}
