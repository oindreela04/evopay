import 'react'

declare module 'react' {
  interface HTMLAttributes<T> {
    initial?: any
    animate?: any
    exit?: any
    transition?: any
    layout?: any
  }
}
