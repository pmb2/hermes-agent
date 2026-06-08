---
name: pytorch-fsdp
description: Expert guidance for Fully Sharded Data Parallel training with PyTorch FSDP - parameter sharding, mixed precision, CPU offloading, FSDP2
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [torch>=2.0, transformers]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Distributed Training, PyTorch, FSDP, Data Parallel, Sharding, Mixed Precision, CPU Offloading, FSDP2, Large-Scale Training]
    triggers: [pytorch, fsdp, distributed-training, sharding, mixed-precision, cpu-offloading, fsdp2, data-parallel, large-scale-training]

---

# Pytorch-Fsdp Skill

Comprehensive assistance with pytorch-fsdp development, generated from official documentation.

## When to Use This Skill

This skill should be triggered when:
- Working with pytorch-fsdp
- Asking about pytorch-fsdp features or APIs
- Implementing pytorch-fsdp solutions
- Debugging pytorch-fsdp code
- Learning pytorch-fsdp best practices

## Quick Reference

This skill was auto-generated from the official PyTorch distributed documentation. The full documentation dump has been extracted to reference files to stay under the SKILL.md size limit.

### Topics Covered

- **Join Context Manager** — `torch.distributed.algorithms.Join`, `Joinable`, `JoinHook` for uneven inputs
- **Distributed Communication** — `torch.distributed` backends (NCCL, Gloo, MPI, XCCL), environment variables
- **Initialization** — `init_process_group()`, `init_device_mesh()`, device mesh setup
- **Groups** — `new_group()`, sub-group creation, multi-communicator management
- **DistributedDataParallel (DDP)** — construction, forward/backward pass, gradient synchronization, static graph mode
- **Debugging** — `monitored_barrier()`, `TORCH_DISTRIBUTED_DEBUG`, `breakpoint()`, distributed logging
- **Launch Utilities** — `torch.distributed.launch`, spawn utility, multi-node configuration

### Using the Reference Files

For detailed API reference, consult the `references/` files:

- `references/other.md` — Deep dives on DDP internals, collective ops, launch utilities, debugging, store types (extracted from official PyTorch docs)

For up-to-date information, the official PyTorch distributed docs are authoritative:
- https://pytorch.org/docs/stable/distributed.html
- https://pytorch.org/docs/stable/fsdp.html

## Reference Files

This skill includes comprehensive documentation in `references/`:

- **other.md** — PyTorch distributed API reference (DDP, collectives, launch utilities, debugging, stores)

Use `view` to read specific reference files when detailed information is needed.

## Working with This Skill

### For Beginners

Start with the tutorials in `references/other.md` for foundational concepts. The topic covers: DDP internals, distributed initialization, process group management, and debugging distributed training.

### For Specific Features

Use the appropriate reference file for detailed information about specific PyTorch distributed APIs.

### For Code Examples

The `references/other.md` file contains code examples extracted from the official PyTorch distributed documentation, including:
- DDP setup and training loops
- Multi-node launch configuration
- NCCL backend tuning
- Debugging with monitored barrier and TORCH_DISTRIBUTED_DEBUG

## Resources

### references/
Organized documentation extracted from official sources. These files contain:
- Detailed explanations
- Code examples with language annotations
- Links to original documentation
- Table of contents for quick navigation

### scripts/
Add helper scripts here for common automation tasks.

### assets/
Add templates, boilerplate, or example projects here.

## Notes

- This skill was automatically generated from official PyTorch distributed documentation
- The Quick Reference section was extracted to `references/other.md` to keep the main SKILL.md under the 100KB size limit
- Reference files preserve the structure and examples from source docs
- Code examples include language detection for better syntax highlighting
- Official PyTorch docs at https://pytorch.org/docs/stable/distributed.html should be consulted for the most current information

## Updating

To refresh this skill with updated documentation:
1. Re-run the scraper with the same configuration
2. The skill will be rebuilt with the latest information
