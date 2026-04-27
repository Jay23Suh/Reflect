const FALLBACK_QUOTE = { q: "Stay grounded.", a: "Ground" }
const ZEN_QUOTES_API = 'https://zenquotes.io/api/today'

export const QuoteService = {
  async getQuoteOfTheDay() {
    const today = new Date().toISOString().split('T')[0]
    const cached = localStorage.getItem('ground_quote_cache')

    if (cached) {
      const { date, quote } = JSON.parse(cached)
      if (date === today) return quote
    }

    try {
      const response = await fetch(ZEN_QUOTES_API)
      const data = await response.json()
      if (data && data[0]) {
        const quote = { q: data[0].q, a: data[0].a }
        localStorage.setItem('ground_quote_cache', JSON.stringify({ date: today, quote }))
        return quote
      }
    } catch {
      // API down — use fallback
    }

    return FALLBACK_QUOTE
  },

  shouldShowModal() {
    const today = new Date().toISOString().split('T')[0]
    const lastShown = localStorage.getItem('ground_quote_last_shown')
    return lastShown !== today
  },

  markQuoteAsShown() {
    const today = new Date().toISOString().split('T')[0]
    localStorage.setItem('ground_quote_last_shown', today)
  },
}
