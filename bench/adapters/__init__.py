"""Adapters: one module per tool under test.

An adapter is a class with:
  name       -- short name used in tables
  versions() -- dict of package name -> version string
  solve(pair)-- returns {output name: (float value, unit string)} with values
               already converted by the tool to the units the reference uses,
               or raises Refused or NotOffered (see bench.outcome).

An adapter may only translate spellings and call the tool. It must never do
the calculation itself: if the tool has no feature for a task, the adapter
raises NotOffered.
"""
