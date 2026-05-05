function isAuthTokenInvalid(error) {
    return error.data == "JWTDecodeError" || error.data == "ExpiredError" || error.data == "DeactivatedError" || error.data == "NotFoundError" || error.data == "SecondFactorRequiredError"
}


  function parseDate(date){
    return new Date(date).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric'
    })
  }

  function parseDateTime(date){
    return new Date(date).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    })
  }
