export const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const formatDuration = (duration) => {
  if (!duration) return 'Unknown';
  
  try {
    // Handle ISO 8601 format (e.g., "PT15M30S")
    if (duration.startsWith('PT')) {
      const time = duration.slice(2);
      const hoursMatch = time.match(/(\d+)H/);
      const minutesMatch = time.match(/(\d+)M/);
      const secondsMatch = time.match(/(\d+)S/);
      
      const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0;
      const minutes = minutesMatch ? parseInt(minutesMatch[1]) : 0;
      const seconds = secondsMatch ? parseInt(secondsMatch[1]) : 0;
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      }
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    
    // Return as-is if not ISO format
    return duration;
  } catch (error) {
    console.error('Error formatting duration:', error);
    return duration;
  }
};

export const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getSimilarityColor = (score) => {
  if (score >= 0.8) return '#00D100'; // Green
  if (score >= 0.6) return '#FFD600'; // Yellow
  return '#FF3333'; // Red
};