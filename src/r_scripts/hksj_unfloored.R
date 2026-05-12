# hksj_unfloored.R — REML + HKSJ, NO Q-floor (raw HKSJ SE on log/standardised scale).
#
# stdin: {"requests": [{"ma_id": "...", "yi": [...], "vi": [...]}, ...]}
# stdout: {"results": [{"ma_id": "...", "estimate": ..., "se": ..., "ci_lo": ...,
#                       "ci_hi": ..., "tau2": ..., "i2": ..., "k": ...,
#                       "converged": true|false, "reason_code": ""}, ...]}
#
# Forked from cochrane-modern-re/src/r_scripts/run_metafor.R; the
# max(HKSJ_SE, Wald_SE) Q-floor block at run_metafor.R:54-67 is intentionally
# OMITTED so the returned SE is the raw HKSJ standard error.

suppressPackageStartupMessages({
  library(metafor)
  library(jsonlite)
})

input <- fromJSON(file("stdin"), simplifyVector = FALSE)

results <- lapply(input$requests, function(req) {
  ma_id <- req$ma_id
  yi <- as.numeric(unlist(req$yi))
  vi <- as.numeric(unlist(req$vi))
  k <- length(yi)

  out <- list(
    ma_id = ma_id, estimate = NA_real_, se = NA_real_,
    ci_lo = NA_real_, ci_hi = NA_real_,
    tau2 = NA_real_, i2 = NA_real_, k = k,
    converged = FALSE, reason_code = ""
  )

  if (k < 2) {
    out$reason_code <- "k_lt_2"
    return(out)
  }
  if (any(vi <= 0)) {
    out$reason_code <- "nonpositive_variance"
    return(out)
  }

  fit <- tryCatch(
    rma(yi = yi, vi = vi, method = "REML", test = "knha", level = 95),
    error = function(e) NULL,
    warning = function(w) {
      suppressWarnings(rma(yi = yi, vi = vi, method = "REML", test = "knha", level = 95))
    }
  )

  # Convergence proxy: fit exists and primary effect estimate is finite.
  # Modern metafor (>=4.0) does not expose $convergence directly.
  if (is.null(fit) || !is.finite(as.numeric(fit$beta)[1])) {
    out$reason_code <- "rma_failed"
    return(out)
  }

  out$estimate <- as.numeric(fit$b)
  out$se      <- as.numeric(fit$se)
  out$ci_lo   <- as.numeric(fit$ci.lb)
  out$ci_hi   <- as.numeric(fit$ci.ub)
  out$tau2    <- as.numeric(fit$tau2)
  out$i2      <- as.numeric(fit$I2)
  out$converged <- TRUE
  out
})

cat(toJSON(list(results = results), auto_unbox = TRUE, digits = NA, na = "null"))
