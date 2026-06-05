import { render, screen } from '@testing-library/react'
import CommandCenter from '../src/app/page'

describe('CommandCenter', () => {
  it('renders a heading with QIYAM text', () => {
    render(<CommandCenter />)
    
    const heading = screen.getByRole('heading', { level: 1 })
    
    expect(heading).toBeInTheDocument()
    expect(heading).toHaveTextContent('قيام (QIYAM)')
  })
})
