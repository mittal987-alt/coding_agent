declare module 'react-syntax-highlighter/dist/esm/styles/prism' {
  const styles: any;
  export = styles;
}

declare module 'react-syntax-highlighter' {
  export const Prism: any;
  export const Light: any;
  export default function SyntaxHighlighter(props: any): any;
}
