# Independent reference: metafor::rma with HKSJ, NO floor.
# Reads tests/fixtures/golden_mas.json (yi/vi only), writes
# tests/fixtures/golden_mas_reference.json with computed un-floored values.

suppressPackageStartupMessages({
  library(metafor)
  library(jsonlite)
})

g <- fromJSON("tests/fixtures/golden_mas.json", simplifyVector = FALSE)
results <- lapply(g, function(item) {
  yi <- unlist(item$yi); vi <- unlist(item$vi)
  fit <- rma(yi = yi, vi = vi, method = "REML", test = "knha", level = 95)
  list(
    ma_id = item$ma_id,
    estimate = as.numeric(fit$b),
    se = as.numeric(fit$se),
    ci_lo = as.numeric(fit$ci.lb),
    ci_hi = as.numeric(fit$ci.ub)
  )
})
writeLines(toJSON(results, auto_unbox = TRUE, digits = NA, na = "null"),
           "tests/fixtures/golden_mas_reference.json")
cat(sprintf("wrote reference for %d MAs\n", length(results)))
