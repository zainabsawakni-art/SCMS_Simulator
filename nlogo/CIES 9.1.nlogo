;  © Islamic Research and Training Institute


globals [
  seed-number        ; Seed for random number generation; can be fixed for reproducible runs.
  total-contribution ; Total membership fee contributions by all customers this period.
  total-deficit      ; Total of unpaid parts of installments for all customers this period.
  total-compensation ; Total (compensation-received + additional-compensation) for all customers.
  month
  total-paid-installment ; Total of parts of installments repaid by customers for this period.
  bank-assets        ; bank-cash + bank-receivables
  bank-receivables   ; All debt not yet received by the bank
  bank-cash          ; Money in the bank - grows when received from the fund (either from customer
                     ; repayments or compensation for repayment deficits); shrinks via new loans.
  fund-assets        ; All-time total membership fee contributions by all customers, ignoring
                     ; deductions due to reserve-ratio or compensation.
  fund-net-assets    ; True fund assets, factoring in compensation paid out to cover insolvency
                     ; and reserves set aside as dictated by reserve-ratio.
  total-debt         ; Total debt still owed to bank.
  zero-risk-period   ; Number of months till non-performing debt = 0
  zero-c-period      ; FIXME: unused
  total-new-debt     ; Total new debt this period due to renew-financing.
  expelled-agents    ; Total number of customers expelled due to 3 late payments.
  cum-total-deficit  ; All-time total deficit which won't ever be repaid by customers and needs
                     ; to be compensated to the bank by the fund.  This only ever goes up.
  cum-total-paid-installment  ; All-time total of parts of installments repaid by customers.
]

; Other global variables set by sliders etc.:
;
;
; fix-random-seed (boolean)
;
;   If true, requires a fixed random seed to be entered to allow
;   reproducible runs.
;
;   FIXME: This doesn't work any more, because the order in which
;   patches are called is non-deterministic with respect to this
;   random seed, which causes two problems:
;
;     1. When the random function is used inside per-patch code,
;        the random number generator applies the same sequence of
;        random numbers to the patches in a different order each time.
;
;     2. Calculations inside per-patch code which depends on values
;        from other patches will be affected by the order in which those
;        values are updated.  Currently this affects calculation of
;        peer pressure in cal-rating in which d2 depends on the b-risk
;        of its neighbours.
;
; base-rate (percentage)
;
;   Base fee for contribution to mutual insurance fund.  Those who pay
;   on day 1 only pay this.  Later payments require a premium on top.
;
; premium-increment (percentage)
;
;   Amount to add to contribution on top of base-rate for each extra
;   day that payment is delayed.
;
; min-installment / max-installment
;
;   Upper/lower bounds on the range of installment amounts due for
;   repayment across all customers.
;
; min-periods / max-periods
;
;   Upper/lower bounds on the number of repayment periods across all
;   customers.  Stop simulation after max-periods if renew-financing
;   is false.
;
; no-of-periods
;
;   Number of periods after which to stop the simulation if
;   renew-financing is true.
;
; renew-financing (boolean)
;
;   If true, renew customers with new loans when they have paid off
;   their debt.  Also determines whether when to stop the simulation
;   (see above).
;
; insolvency-risk (percentage)
;
;   Probability of any customer being able to repay any given installment
;   in full.  Recalculated for each customer each period.
;
; unpaid-fraction (percentage)
;
;   Average fraction of installment which will go as an unpaid deficit
;   when a customer is hit by an insolvency "shock".
;   insolvency-fraction is the per-patch per-period value randomly
;   calculated from this based on the randomness global.
;
; max-day (1 to 30)
;
;   The first payment day which is considered as unacceptably late,
;   counting possible payment days from day 1 where only the base-rate
;   is charged, and no premium.  In other words, the latest payment
;   day which is still acceptable without missing the deadline is
;   (max-day - 1).
;
;   If the customer's payment exceeds this payment deadline three
;   times (not necessarily in a row; an on-time payment does not reset
;   the late-payment count), they are expelled from the network. See
;   late-payment, membership, and expelled-agents variables.
;
; p-day-response
;
;   Weighting factor specifying on average how relevant the original
;   unadjusted preferred payment day is in determining the adjusted
;   payment day, relative to the other factors, i.e. response
;   (aversion) to additional premium costs, and the effect of
;   influence from peers.  alpha-1 is the corresponding per-patch
;   value with random deviation.
;
; premium-response
;
;   Weighting factor specifying on average how much the customer's
;   preferred payment day should be adjusted based on their aversion
;   to paying an increased premium due to lateness.  alpha-2 is the
;   corresponding per-patch value with random deviation.
;
; peer-effect
;
;   Weighting factor specifying on average how much the customer's
;   preferred payment day should be adjusted based on the mean
;   behavioural risk of the customer's neighbours.  lamda is the
;   corresponding per-patch value with random deviation.
;
; reserve-ratio
;
;   Percentage of fund assets to set aside before any compensation
;   is taken out.
;
; compensation-ratio
;
;   This percentage is used in two ways:
;
;     1. as a threshold percentage of the fund's net assets: if the
;        total unpaid deficit in customer repayments within a period
;        which should be compensated back to the lender is less than
;        this percentage of the fund's net assets, then all deficits
;        within the period will be fully compensated, and
;
;     2. as a percentage of the total *deficit*: if the total deficit
;        is *more* than this percentage of the fund's net assets, then
;        only this percentage of the *deficit* will be compensated.
;
; adjust-compensation (boolean)
;
;   If true, whenever the net assets of the fund exceed the total
;   deficits, accumulated deficits still due to the lender are paid.
;   This happens after any deficits from the current period may have
;   been compensated according to compensation-ratio, and is not
;   gated by compensation-ratio in the same way that compensations
;   for the current period are.
;
; randomness
;
;   Percentage used to determine bounds of random distribution
;   for values for each patch around a global value:
;
;     - lamda value around peer-effect
;     - insolvency-fraction around unpaid-fraction
;     - alpha-1 around p-day-response
;     - alpha-2 around premium-response
;

patches-own [
  i                        ; Unique index of customer, starting bottom left,
                           ; going rightwards then upwards and ending top right

  installment              ; Periodic repayment due

  duration                 ; Number of periods for this loan,
                           ; random between {min,max}-installment.

  shock                    ; 1 or 0, decided by insolvency-risk.  Once set, dictates
                           ; whether insolvency-fraction will have any impact for
                           ; how much is paid of a) installment for this period, and
                           ; b) the membership contribution for the next period.

  insolvency-fraction      ; Once set, dictates the deficit (i.e. unpaid) fraction
                           ; of a) installment for this period, and b) the membership
                           ; contribution for the next period.

  ; Set in cal-contribution:
  paid-contribution        ; Amount paid for membership fee by customer this period
                           ; (calculated as d-contribution % of installment repayment).
  cum-paid-contribution    ; Total amount paid for membership fee by customer.

  cumulative-installment   ; Total of installments so far (paid or otherwise)

  ; Set in cal-insolvency:
  paid-installment         ; Part of installment repaid by customer for this period.
  cum-paid-installment     ; Total repaid by customer
  deficit                  ; Part of installment unpaid by customer for this period.
  cumulative-deficit       ; Total accumulated deficit in repayments to lender from
                           ; this customer, taking into account full history
                           ; including any deductions due to the fund paying out
                           ; compensation.

  compensation-share       ; Fraction of deficit owed by this customer to the lender
                           ; which will be compensated from fund reserves. Calculated
                           ; in cal-shares and used in cal-compensation.  Currently
                           ; the same for all customers even though it's a per-patch
                           ; variable.

  compensation-received    ; Repayment to lender for this customer this period
  cum-compensation         ; Total repayments to lender for this customer

  debt                     ; Amount of loan for this customer still payable
                           ; (assumes fund will eventually compensate all deficits)
  cum-debt                 ; Total of all loans to this customer.
  additional-compensation  ; How much of previously accumulated deficit gets compensated
                           ; by the fund this period, on top of compensation for any
                           ; deficit for this period
  share               ; Fraction of overall additional compensation to be covered by
                      ; the fund for this customer this period.  (FIXME: Should be a local?)
  balance             ; Consistency check to ensure that installment == paid-installment - deficit
  financing-round     ; Count of how many times this customer has been financed (starts at 1).
  count-new-debt      ; Count of how many times this customer has been refinanced (starts at 0).
  patch-month         ; How many months the customer is into the current loan (starts at 1).
  patch-new-debt      ; Any new debt incurred for this patch due to renew-financing.
  performing-debt     ; Same as debt
  non-performing-debt ; Debt which won't ever be repaid and will still have to be
                      ; compensated by the fund.
  gross-debt          ; Size of the initial loan (unaffected by repayments / compensation).

  d                   ; Non-adjusted preferred pay-day, fixed in setup-payment-day.
  p-day               ; d±1, randomly varied per period in cal-payment-day

  day                 ; Actual pay-day for period, adjusted according to incentives;
                      ; by calculating adjusted behavioural risk (b-risk) and then
                      ; scaling back up to days: round (b-risk * 30)

  b-risk              ; Weighted average of d1 and d2, with lamda as the weighting
                      ; factor for peer pressure - how much to adjust b-risk to
                      ; mimic neighbours' b-risk.
                      ;
                      ; d1 is weighted combination of p-day and std-premium,
                      ; weighted by alpha-1 and alpha-2 respectively.
                      ;
                      ; d2 is mean b-risk of neighbours

  lamda               ; Weighting factor for peer pressure - how much to adjust
                      ; b-risk to mimic neighbours' b-risk.  Randomly distributed
                      ; around peer-effect by randomness % in setup-peer-effect.

  d-contribution      ; Contribution to fund based on day (adjusted payment day).

  std-contribution    ; Contribution scaled to percentage of 30 * base-rate
                      ; (FIXME: should be base-rate + 29 * premium-increment?)
                      ; See cal-premium.

  std-premium         ; Same as std-contribution, but excluding the first day.

  alpha-1             ; Weighting factor for adherence to original p-day, randomly
                      ; distributed by randomness % around p-day-response

  alpha-2             ; Weighting factor for avoiding premium, randomly distributed
                      ; by randomness % around premium-response

  points              ; Points awarded for latest payment (not yet accumulated).

  membership          ; 1 if still in the network; 0 if expelled.
  on-time-payment     ; Number of times the customer has paid on time.
  late-payment        ; Number of times max-day payment deadline missed.

  status             ; status of the patch (agent). Equals 1 if the agent is receiving financing; zero otherwise.

  unpaid-contribution

]


to setup
  show "-------------------------------------------------------------------"
  clear-all
  set-random-seed

  setup-patches
  if incentive-system = true [setup-incentive-system]
  setup-bank
  setup-fund
  reset-ticks
end

to set-random-seed
  set seed-number new-seed
  if fix-random-seed [
    let input-seed-number user-input "Type a seed number"
    set seed-number read-from-string input-seed-number
  ]
  random-seed seed-number
  print (word "Seed number = " seed-number)
  print (word "Start at " date-and-time)
end

to setup-patches
  cal-no-of-customers
  ask patches [
    setup-financing
    set financing-round 1
    set membership 1
  ]
end


to cal-no-of-customers
  let max-x (sqrt(world-size) - 1)/ 2
  let min-x max-x * -1
  let max-y max-x
  let min-y min-x
  resize-world min-x max-x min-y max-y ;

  ask patches [
    set i (pxcor - min-pxcor) * world-width + (pycor - min-pycor)
  ]
end

to setup-financing  ; a patch procedure
  ; installment is any where from min to max installment. We add 1
  ; because integer random function in NetLogo generates up to number
  ; minus 1.
  set installment  min-installment + (random (max-installment - min-installment + 1))

  ; duration is any where from min-periods to max-periods
  set duration min-periods + (random (max-periods - min-periods))

  set debt installment * duration
  set cum-debt cum-debt + debt
  set gross-debt installment * duration
  set pcolor scale-color cyan (debt / (installment + 1)) 50 10
end


to setup-incentive-system
  ask patches [
    setup-payment-day
    setup-contribution
    setup-peer-effect
    setup-response
    setup-membership
  ]
end

to setup-payment-day ; a patch procedure
  ; this sets the average day of payment for each agent to be any
  ; where from day 1 to day max-day of the month
  set d (random max-day) + 1

  set p-day d   ; preferred day of payment
  set day p-day ; actual day of payment is set initially to preferred day
  set b-risk (day / 30) ; this is initial behavioral risk
end

to setup-contribution ; a patch procedure
  ; initial contribution rate
  set d-contribution (base-rate / 100) + ((premium-increment / 100) * max (list (d - 1) 1))

  if base-rate > 0 [
    ; this is initial standardized contribution
    set std-contribution (d-contribution / (base-rate / 100)) / 30
  ]
  if base-rate = 0 [
    set std-contribution 0
  ]
end

to setup-peer-effect ; a patch procedure
  let var (randomness / 100)
  let min-lamda (1 - var) * (peer-effect / 100)
  let max-lamda (1 + var) * (peer-effect / 100)
  ; lamda is distributed around peer-effect
  set lamda min-lamda + random-float (max-lamda - min-lamda)
  if lamda < 0 [set lamda 0]
  if lamda > 1 [set lamda 1]
end

to setup-response ; a patch procedure
  let var (randomness / 100)
  let min-alpha-1 (1 - var) * p-day-response
  let max-alpha-1 (1 + var) * p-day-response
  let min-alpha-2 (1 - var) * premium-response
  let max-alpha-2 (1 + var) * premium-response
  ; alpha-1 is uniformly distributed around p-day (preferred day) response.
  set alpha-1 min-alpha-1 + random-float (max-alpha-1 - min-alpha-1)
  ; alpha-2 is uniformly distributed around premium-response.
  set alpha-2 min-alpha-2 + random-float (max-alpha-2 - min-alpha-2)
end

to setup-membership ; a patch procedure
  set points 100 - (d - 1)
  set on-time-payment 0
  set late-payment 0
  set membership 1
end

to setup-bank
  set total-debt sum [debt] of patches
  set bank-receivables total-debt
  set bank-cash 0
  set bank-assets bank-cash + bank-receivables
end

to setup-fund
  set fund-net-assets 100
  set fund-assets fund-net-assets
end

to color-patches
    set pcolor scale-color cyan ((performing-debt + non-performing-debt) / (installment + 1)) 50 10
end

to cal-renew-financing
  ask patches [
    if (patch-month > duration or membership = 0)  [
      ifelse renew-financing = true [
        clear-vars
        setup-membership
        setup-financing
        set status 1
        set financing-round financing-round + 1
        set patch-new-debt debt
        set count-new-debt count-new-debt + 1
        set patch-month 1
      ] [
        cal-exit
      ]
    ]
  ]
  set total-new-debt sum [patch-new-debt] of patches
  ask patches [set patch-new-debt 0]
end

to cal-contribution
  ask patches [
    ifelse (patch-month <= duration and membership = 1) [
      ; Calculate how much of membership premium the customer will
      ; contribute to the fund for mutual insurance.
      ;
      ; This is calculated as a percentage of the customer's full or
      ; part repayment of the monthly installment, so we first need to
      ; calculate that:
      let prev-installment (1 - (shock * insolvency-fraction)) * installment

      ; N.B. This is run before cal-shock, whereas cal-insolvency is
      ; run after.  This means that contributions calculated here
      ; relate to the previous month's payment.
      ;
      ; That's why a bit later the same calculation is made and
      ; assigned to paid-installment in cal-insolvency, which also
      ; assigns the opposite (how much they *won't* pay) to the
      ; deficit variable, as well as cumulative totals for both.

      ; d-contribution is the percentage of the previous month's
      ; repayment which the user will make as a contribution to
      ; membership.  If the incentive system is enabled, this is
      ; already calculated by cal-premium which is called by
      ; cal-incentives just before this function (cal-contribution) is
      ; called.
      if incentive-system = false [
        set d-contribution (base-rate / 100)
      ]
      set paid-contribution d-contribution * prev-installment

      set cumulative-installment cumulative-installment + installment
      set cum-paid-contribution cum-paid-contribution + paid-contribution
    ] [
      set paid-contribution 0
    ]
  ]
  set total-contribution sum [paid-contribution] of patches
end


to cal-payment-day ; a patch procedure
  let min-p-day max (list (d - 1) 1)
  let max-p-day d + 1
  ; p-day is preferred payment day = d plus or minus one day
  set p-day min-p-day + random (max-p-day - min-p-day + 1)
  if p-day > max-day + 1 [set p-day max-day + 1]
end

to cal-rating ; a patches procedure
  ask patches [
    if (patch-month <= duration and membership = 1) [
      cal-payment-day
      let d1 (alpha-1 * (p-day / 30)) - (alpha-2 * std-premium)
      let d2 mean [b-risk] of neighbors

      ; b-risk is behavioral risk = 1 / day of payment
      set b-risk ((1 - lamda) * d1) + (lamda * d2)

      if b-risk < (1 / 30) [
        set b-risk 1 / 30
      ]
      ; day is the actual payment day. p-day is the preferred payment day.
      set day round (b-risk * 30)
      cal-membership
    ]
  ]
end


to cal-premium
    ask patches [
     if (patch-month <= duration and membership = 1) [
      ; this calculates the contribution based on the day of payment.
      set d-contribution (base-rate / 100) + ((premium-increment / 100) * (day - 1))
      if base-rate > 0 [
        ; this standardizes d-contribution to be of the same scale as
        ; of the day of payment as a fraction of 30.
        set std-contribution (d-contribution / (base-rate / 100)) / 30
        ; the premium is the contribution above and over the base contribution rate.
        set std-premium std-contribution - (1 / 30)
      ]
      if base-rate = 0 [
        set d-contribution 0
        set std-contribution 0
        set std-premium 0
      ]
    ]
  ]
end


to cal-membership ; a patch procedure
  set points 100 - (day - 1)
  ifelse points >= 100 - (max-day - 2) [
    set on-time-payment on-time-payment + 1
  ] [
    set late-payment late-payment + 1
  ]
  ifelse late-payment > 3 [
    set membership 0
    set expelled-agents expelled-agents + 1
  ] [
    set membership 1
  ]
end


to cal-incentives
  cal-rating
  cal-premium
end


to cal-shock
  ask patches [
    if (patch-month <= duration and membership = 1) [
      let s (random 100) + 1
      ifelse s <= insolvency-risk [
        set shock 1
        let var (randomness / 100)
        let min-fraction (1 - var) * (unpaid-fraction / 100)
        let max-fraction (1 + var) * (unpaid-fraction / 100)
        ; this will give a uniformly distributed fraction around the unpaid-fraction
        set insolvency-fraction min-fraction + random-float (max-fraction - min-fraction)
        if insolvency-fraction > 1 [
          set insolvency-fraction 1
        ]
      ] [
        set shock 0
        set insolvency-fraction 0
      ]
      ifelse shock = 1 [
        set pcolor red
      ] [
        color-patches
      ]
    ]
  ]
end


to cal-insolvency
  cal-shock
  ask patches [
    if (patch-month <= duration and membership = 1) [
      set deficit shock * insolvency-fraction * installment
      set cumulative-deficit cumulative-deficit + deficit
      set paid-installment installment - deficit
      set cum-paid-installment cum-paid-installment + paid-installment
    ]

    if (patch-month > duration or membership = 0) [
      set deficit 0
      set paid-installment 0
    ]
  ]
  cal-totals
end


to cal-totals
  set total-deficit sum [deficit] of patches
  if total-deficit < 0 [
    user-message (word "Warning: total-deficit " total-deficit)
  ]
  set total-paid-installment sum [paid-installment] of patches
  set cum-total-paid-installment cum-total-paid-installment + total-paid-installment
  set cum-total-deficit cum-total-deficit + total-deficit
  cal-shares
end

to cal-shares
  ; Calculate compensation shares.
  ;
  ; If the fund can afford to compensate the total deficit in
  ; repayments for this period, then set compensation-share to the
  ; fraction of the deficit for each customer which will be
  ; compensated.  This fraction will either be 1 if the total deficit
  ; is less than compensation-ratio% of the fund's net assets, or
  ; otherwise it will be compensation-ratio%.  So for example if
  ; compensation-ratio is 70%, if the total deficit is less than 70%
  ; of the fund's net assets, then all deficits will be fully
  ; compensated, or if the deficit is between 70% and 100% of the
  ; fund's net assets, 70% will be compensated.
  ;
  ; FIXME: even though compensation-share is a patch variable, it's
  ; currently always the same for every customer, so it could be made
  ; into a global.
  ifelse fund-net-assets > total-deficit [
    ifelse (total-deficit / fund-net-assets) < (compensation-ratio / 100) [
      ask patches [set compensation-share 1]
    ] [
      ask patches [set compensation-share (compensation-ratio / 100)]
    ]
  ] [
    ask patches [set compensation-share 0]
  ]
end


to cal-compensation
  ask patches [
    if (patch-month <= duration and membership = 1) [
      set compensation-received (compensation-share * deficit)
      if compensation-received > deficit [
        user-message "Warning: compensation-received > deficit"
      ]
      set cumulative-deficit cumulative-deficit - compensation-received
      set cum-compensation cum-compensation + compensation-received
      set non-performing-debt cumulative-deficit
      if (compensation-share > 1) or (compensation-share < 0) [
        user-message "Warning: compensation-share exceeds bounds"
      ]
    ]
    if (patch-month > duration or membership = 0) [
      set compensation-received 0
    ]
  ]
  adjust-compensations
  let sum-period sum [compensation-received] of patches
  let sum-additional sum [additional-compensation] of patches
  set total-compensation sum-period + sum-additional
end


; Pay past accumulated deficits if there is enough assets in the fund.
to adjust-compensations
  ifelse adjust-compensation = true [
    let sum-cum-deficit sum [cumulative-deficit] of patches
    ifelse fund-net-assets > sum-cum-deficit [
      ; How much surplus would we have left if we compensated all previously
      ; accumulated deficits right now?
      let fund-surplus fund-net-assets - sum-cum-deficit
      ask patches [
        ; What fraction of the overall deficit does this patch own?
        set share cumulative-deficit / (sum-cum-deficit + 1)
        if (share > 1) or (share < 0) [
          user-message "Warning: share exceeds bounds"
        ]
        ifelse (patch-month <= duration and membership = 1) [
          ; FIXME: shouldn't this be the share of fund-net-assets?  Why compensate slower?
          ; Is it to smooth the rate of compensation?
          ; let uncapped-add-comp share * fund-net-assets
          let uncapped-add-comp share * fund-surplus
          set additional-compensation min (list uncapped-add-comp cumulative-deficit)
          ; update cumulative-deficit
          set cumulative-deficit cumulative-deficit - additional-compensation
          if cumulative-deficit < 0 [
            set cumulative-deficit 0
          ]
          set cum-compensation cum-compensation + additional-compensation
          set non-performing-debt cumulative-deficit
        ] [
          set additional-compensation 0
        ]
      ]
    ] [
      ask patches [set additional-compensation 0]
    ]
  ] [
    ask patches [set additional-compensation 0]
  ]
end


to cal-debt
  ask patches [
    if (patch-month <= duration and membership = 1) [
      set debt max (list (debt - installment) 0)
      set performing-debt debt
    ]
  ]
end


to check-consistency
  ask patches [
    if (patch-month <= duration and membership = 1) [
      set balance installment - paid-installment - deficit; balance must be zero.
    ]
  ]
end


to cal-bank
  set bank-cash bank-cash + total-paid-installment + total-compensation - total-new-debt
  if bank-cash < 0 [
    user-message (word "Warning: bank-cash < 0")
  ]
  set bank-receivables sum [performing-debt] of patches + sum [non-performing-debt] of patches
  set bank-assets bank-cash + bank-receivables
end

to cal-fund
  set fund-assets fund-assets + total-contribution
  set fund-net-assets max (list ((1 - (reserve-ratio / 100)) * fund-assets - total-compensation) 0)
  if fund-assets < total-compensation [
    user-message (word "Warning: fund net assets: " (fund-assets - total-compensation))
  ]
end


to clear-vars ; a patch procedure
  set status 0
  set installment 0
  set paid-contribution 0
  set deficit 0
  set paid-installment 0
  set compensation-received 0
  set additional-compensation 0
  set patch-new-debt 0
  set debt 0
  set d-contribution 0
  set std-contribution 0
  set std-premium 0
  set day 0
  set b-risk 0
  set on-time-payment 0
  set late-payment 0
end


to cal-exit ; a patch procedure
   clear-vars
   color-patches
end


to cal-zero-period
  ; calculate the number of months till non-performing debt = 0
  ifelse mean [non-performing-debt] of patches > 0 [
    set zero-risk-period month
  ] [
    stop
  ]
end


to go
  set month month + 1
  ask patches [set patch-month patch-month + 1]
  cal-renew-financing
  if incentive-system = true [cal-incentives]
  cal-contribution
  cal-insolvency
  cal-compensation
  cal-debt
  cal-fund
  cal-bank
  check-consistency
  cal-zero-period
  ifelse renew-financing = false
   [if month = max-periods [stop]]
   [if month = no-of-periods [stop]]
  tick
end
@#$#@#$#@
GRAPHICS-WINDOW
5
10
336
342
-1
-1
9.23
1
10
1
1
1
0
1
1
1
-17
17
-17
17
1
1
1
ticks
30.0

SLIDER
359
72
536
105
world-size
world-size
100
5000
1225.0
25
1
NIL
HORIZONTAL

BUTTON
361
34
427
67
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
427
34
493
67
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
1021
43
1193
76
base-rate
base-rate
0
.5
0.2
0.01
1
%
HORIZONTAL

SLIDER
359
150
531
183
insolvency-risk
insolvency-risk
0
25
3.0
0.5
1
%
HORIZONTAL

SLIDER
1025
375
1197
408
compensation-ratio
compensation-ratio
0
100
70.0
5
1
%
HORIZONTAL

MONITOR
425
485
482
530
month
month
0
1
11

MONITOR
986
412
1075
457
fund total-assets
fund-assets / count patches
3
1
11

MONITOR
1075
412
1159
457
fund net-assets
fund-net-assets / count patches
3
1
11

SLIDER
359
247
531
280
min-installment
min-installment
0
10000
4200.0
100
1
$
HORIZONTAL

SLIDER
359
215
531
248
max-installment
max-installment
500
10000
5400.0
100
1
$
HORIZONTAL

SLIDER
359
315
532
348
min-periods
min-periods
12
60
20.0
1
1
NIL
HORIZONTAL

SLIDER
359
280
531
313
max-periods
max-periods
12
90
60.0
1
1
NIL
HORIZONTAL

MONITOR
359
104
532
149
No. of customers
count patches
0
1
11

MONITOR
117
395
221
440
performing debt
mean [performing-debt] of patches
3
1
11

MONITOR
220
395
324
440
non-performing debt
mean [non-performing-debt] of patches
3
1
11

PLOT
538
10
974
182
Compensations
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"comp" 1.0 0 -13840069 true "" "plot mean [compensation-received] of patches"
"deficit" 1.0 0 -8053223 true "" "plot mean [deficit] of patches"
"add comp" 1.0 0 -7500403 true "" "plot mean [additional-compensation] of patches"

PLOT
538
182
974
357
Fund (per capita)
NIL
NIL
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"assets" 1.0 0 -13345367 true "" "plot fund-assets / count patches"
"net ass" 1.0 0 -11221820 true "" "plot fund-net-assets / count patches"
"NPLs" 1.0 0 -955883 true "" "plot mean [non-performing-debt] of patches"
"Reserves" 1.0 0 -7500403 true "" "plot (reserve-ratio / 100) * fund-net-assets / count patches"

MONITOR
250
440
324
485
insolvent agents
count patches with [shock = 1]
0
1
11

SWITCH
360
383
532
416
adjust-compensation
adjust-compensation
0
1
-1000

SWITCH
359
416
532
449
fix-random-seed
fix-random-seed
0
1
-1000

MONITOR
989
506
1049
551
balance
mean [balance] of patches
6
1
11

MONITOR
12
351
116
396
bank-assets
bank-assets / count patches
2
1
11

MONITOR
116
351
220
396
bank-cash
bank-cash / count patches
2
1
11

MONITOR
220
351
324
396
bank-receivables
bank-receivables / count patches
2
1
11

SWITCH
360
448
532
481
renew-financing
renew-financing
0
1
-1000

MONITOR
482
485
532
530
rounds
max [financing-round] of patches
1
1
11

MONITOR
1049
506
1157
551
receivables-check
(bank-receivables - sum [performing-debt] of patches - sum [non-performing-debt] of patches) / count patches
6
1
11

TEXTBOX
991
486
1141
504
Consistency checks
11
0.0
1

MONITOR
1159
412
1249
457
reserves
(reserve-ratio / 100) * fund-assets / count patches
3
1
11

SLIDER
1025
343
1197
376
reserve-ratio
reserve-ratio
0
100
0.0
1
1
%
HORIZONTAL

MONITOR
12
396
116
441
zero-risk period
zero-risk-period
1
1
11

MONITOR
1156
506
1243
551
Bank-assets
(bank-assets - bank-receivables - bank-cash)
6
1
11

SLIDER
359
182
531
215
unpaid-fraction
unpaid-fraction
50
100
70.0
1
1
%
HORIZONTAL

SLIDER
360
349
532
382
No-of-periods
No-of-periods
0
1000
90.0
10
1
NIL
HORIZONTAL

SLIDER
1021
108
1193
141
peer-effect
peer-effect
0
100
40.0
1
1
%
HORIZONTAL

MONITOR
12
485
91
530
payment day
mean [day] of patches
2
1
11

MONITOR
155
485
250
530
contribution %
100 * mean [d-contribution] of patches
3
1
11

SLIDER
1021
75
1193
108
max-day
max-day
5
30
25.0
1
1
NIL
HORIZONTAL

MONITOR
12
440
71
485
A-rated 
count patches with [day >= 1 and day < 11]
2
1
11

MONITOR
70
440
123
485
B-rated
count patches with [day > 10 and day < 20]
2
1
11

SWITCH
1021
10
1193
43
incentive-system
incentive-system
0
1
-1000

SLIDER
1021
285
1193
318
randomness
randomness
5
95
25.0
1
1
%
HORIZONTAL

SLIDER
1021
186
1193
219
premium-increment
premium-increment
0
0.15
0.1
.05
1
%
HORIZONTAL

MONITOR
91
485
156
530
max day
max [day] of patches
1
1
11

SLIDER
1021
219
1193
252
p-day-response
p-day-response
0.5
1.5
1.0
0.1
1
NIL
HORIZONTAL

SLIDER
1021
252
1193
285
premium-response
premium-response
0.5
1.5
1.0
0.1
1
NIL
HORIZONTAL

MONITOR
122
440
177
485
C-rated
count patches with [day >= 20]
2
1
11

MONITOR
250
485
324
530
max contribution %
100 * max [d-contribution] of patches
2
1
11

PLOT
538
357
813
538
rating
NIL
NIL
0.0
3.0
0.0
10.0
true
false
"set-plot-y-range 0 count patches\nset-plot-x-range 0 3\n" "  plot-pen-reset\n  ;set-plot-pen-color green \n  plot count patches with [day < 11]\n  ;set-plot-pen-color blue\n  plot count patches with [day > 10 and day < 20]\n  ;set-plot-pen-color red\n  plot count patches with [day >= 20]"
PENS
"pen-0" 1.0 1 -7500403 false "" ""

TEXTBOX
588
520
635
538
A-rated
11
0.0
1

TEXTBOX
672
521
717
539
B-rated
11
0.0
1

TEXTBOX
747
521
790
539
C-rated
11
0.0
1

MONITOR
425
529
532
574
expelled-agents
expelled-agents
1
1
11

MONITOR
177
440
250
485
avg points
mean [points] of patches
2
1
11

@#$#@#$#@
## WHAT IS IT?

This is a model of integrated credit insurance, rating and incentive system.

## HOW IT WORKS

See attached document.

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.1.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="experiment 3" repetitions="3" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="91"/>
    <metric>count patches with [day &gt;= 1 and day &lt; 11]</metric>
    <metric>count patches with [day &gt; 10 and day &lt; 20]</metric>
    <metric>count patches with [day &gt;= 20]</metric>
    <metric>seed-number</metric>
    <metric>bank-assets / count patches</metric>
    <metric>mean [day] of patches</metric>
    <metric>zero-risk-period</metric>
    <enumeratedValueSet variable="max-installment">
      <value value="5400"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fix-random-seed">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="min-periods">
      <value value="20"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="peer-effect">
      <value value="40"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="premium-response">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="randomness">
      <value value="25"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="incentive-system">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="unpaid-fraction">
      <value value="70"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="No-of-periods">
      <value value="90"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="p-day-response">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="renew-financing">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="world-size">
      <value value="1225"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="base-rate">
      <value value="0.2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="adjust-compensation">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="premium-increment">
      <value value="0.1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="reserve-ratio">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-periods">
      <value value="60"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="insolvency-risk">
      <value value="3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="compensation-ratio">
      <value value="70"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="min-installment">
      <value value="900"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-day">
      <value value="25"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
