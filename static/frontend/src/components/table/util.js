const sortDate = (a, b) => {
    const date_a = a.split("/");
    const date_b = b.split("/");
    return date_a[2] == date_b[2]
      ? date_a[1] == date_b[1]
      ? date_a[0] == date_b[0]
      ? 0
      : Number(date_a[0]) - Number(date_b[0])
      : Number(date_a[1]) - Number(date_b[1])
      : Number(date_a[2]) - Number(date_b[2]);
  }

  export  { sortDate }
