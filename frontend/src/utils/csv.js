function parseLine(line) {
  const result = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim())
      current = ''
    } else {
      current += char
    }
  }
  result.push(current.trim())
  return result
}

export function parseCSV(text) {
  const lines = text.trim().split('\n')
  const headers = parseLine(lines[0])
  return lines.slice(1).map(line => {
    const values = parseLine(line)
    return headers.reduce((obj, header, i) => {
      obj[header] = values[i] ?? ''
      return obj
    }, {})
  })
}

export function toCSVString(data) {
  if (!data.length) return ''
  const headers = Object.keys(data[0])
  const rows = data.map(row =>
    headers.map(h => `"${(row[h] || '').replace(/"/g, '""')}"`).join(',')
  )
  return [headers.join(','), ...rows].join('\n')
}

export function downloadCSV(data, filename) {
  const blob = new Blob([toCSVString(data)], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
