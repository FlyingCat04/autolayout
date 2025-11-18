"""
Line Balancer Module
====================

This module contains the new line balancing algorithm implementation based on the specified requirements:
I. Mục tiêu của cân bằng chuyền bao gồm:
- Sử dụng tất cả các công nhân được nhập vào
- Tất cả công đoạn được nhập vào phải được thực hiện
- Phân bổ công nhân làm công đoạn phù hợp để tổng sản lượng trung bình hàng giờ của các công đoạn tương đương nhau, độ lệch sản lượng giữa 2 công đoạn có sản lượng lớn nhất và nhỏ nhất không quá 10%
- Hiệu suát cân bằng chuyền (phần trăm sản lượng hàng giờ giữa công đoạn bottleneck so với sản lượng hàng giờ mục tiêu) phải lớn hơn hoặc bằng 85%

II. Thuật toán mong muốn:
- Bước 1: Tính toán actual time thực hiện của từng công nhân theo từng công đoạn :actual time = SAM công đoạn * hệ số thông thạo của công nhân theo loại máy của công đoạn
- Bước 2: Tính số người cần của mỗi công đoạn: Số người cần của mỗi công đoạn = Tổng số lượng công nhân được nhập *  SAM của công đoạn đó / Tổng SAM của tất cả các công đoạn được nhập
- Bước 3: Tính được sản lượng hàng giờ mong muốn của cả chuyền, takt time
- Bước 4: Dựa trên nhu cầu người cần của mỗi công đoạn (làm tròn, loại trừ các trường hợp dưới 0.5 người), độ khó và loại máy, phân bổ công nhân thích hợp và số người thích hợp
- Bước 5: Sau khi thực hiện bước 4 xong, thì xem lại các công đoạn có sản lượng hàng giờ vượt mức sản lượng mục tiêu. San bớt năng lực các công đoạn dư thừa sang các công đoạn bottleneck
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
from typing import List, Dict, Any


class LineBalancer:
    """Line balancing component for optimizing work assignments"""
    
    def __init__(self, main_app):
        self.main_app = main_app
    
    def balance_line(self):
        """Balance the production line according to the new algorithm"""
        if not self.main_app.operations:
            messagebox.showwarning("Cảnh báo", "Chưa có công đoạn nào!")
            return
        
        if not self.main_app.workers:
            messagebox.showwarning("Cảnh báo", "Chưa có công nhân nào!")
            return
        
        if len(self.main_app.workers) < 2:
            messagebox.showwarning("Cảnh báo", "Cần ít nhất 2 công nhân để cân bằng chuyền!")
            return
        
        try:
            # Clear previous assignments
            self.main_app.assignments = []
            
            # Step 1: Handle assigned workers first as priority assignments
            assigned_workers_set = self._handle_assigned_workers()
            
            # Step 2: Calculate actual time for each worker on each operation
            worker_operation_times = self._calculate_worker_operation_times()
            
            # Step 3: Calculate required workers for each operation
            operation_worker_requirements = self._calculate_operation_worker_requirements()
            
            # Step 4: Calculate target hourly output and takt time
            target_hourly_output, takt_time = self._calculate_target_output_and_takt_time()
            
            # Step 5: Allocate workers to operations
            self._allocate_workers_to_operations(worker_operation_times, operation_worker_requirements)
            
            # Step 6: Optimize allocations to meet targets
            self._optimize_allocations(target_hourly_output)
            
            # Calculate efficiency statistics
            self._calculate_efficiency_stats()
            
            # Display results
            self.main_app.display_results()
            
            # Refresh charts
            if hasattr(self.main_app, 'charts_tab'):
                self.main_app.charts_tab.refresh_charts()
            
            # Show summary
            self._show_balance_summary(takt_time, target_hourly_output)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Lỗi", f"Lỗi khi cân bằng chuyền: {str(e)}\n\nChi tiết lỗi:\n{error_details}")
    
    def _handle_assigned_workers(self):
        """
        Handle operations with assigned workers first as priority assignments
        """
        # Create a set of assigned workers to track them
        assigned_workers_set = set()
        
        # Process operations with assigned workers
        for operation in self.main_app.operations:
            # Get assigned workers list (up to 4 workers)
            assigned_worker_names = operation.get('assigned_workers', ['', '', '', ''])
            # Ensure we have exactly 4 elements
            while len(assigned_worker_names) < 4:
                assigned_worker_names.append('')
            
            # Process each assigned worker
            for assigned_worker_name in assigned_worker_names:
                if not assigned_worker_name:
                    continue
                    
                # Find the assigned worker
                assigned_worker = None
                for worker in self.main_app.workers:
                    if worker['name'] == assigned_worker_name:
                        assigned_worker = worker
                        break
                
                # If worker is found, create assignment
                if assigned_worker:
                    # Check if worker can handle operation based on difficulty level
                    worker_difficulty = assigned_worker.get('difficulty_handling', 'Dễ')
                    op_difficulty = operation.get('difficulty', 'Dễ')
                    
                    if not self._can_handle_difficulty(worker_difficulty, op_difficulty):
                        # Worker cannot handle this difficulty level
                        messagebox.showwarning(
                            "Cảnh báo", 
                            f"Công nhân {assigned_worker_name} không thể xử lý công đoạn '{operation['name']}' do độ khó không phù hợp!"
                        )
                        continue
                    
                    # Get worker skill level for this machine type (0-5)
                    machine_type = operation.get('machine', '')
                    skill_level = assigned_worker['skills'].get(machine_type, 0)
                    
                    # Check if worker has skill for this machine
                    if skill_level <= 0:
                        messagebox.showwarning(
                            "Cảnh báo", 
                            f"Công nhân {assigned_worker_name} không có kỹ năng cho loại máy '{machine_type}' trong công đoạn '{operation['name']}'!"
                        )
                        continue
                    
                    # Convert skill level to efficiency percentage
                    # Skill levels: 0=Can't use, 1=Learning, 2=Basic, 3=Average, 4=Good, 5=Excellent
                    # Updated scale according to new requirements:
                    # 0 (Không biết dùng): 0% hiệu suất
                    # 1 (Đang học): 30% hiệu suất
                    # 2 (Cơ bản): 50% hiệu suất
                    # 3 (Trung bình): 65% hiệu suất
                    # 4 (Khá): 85% hiệu suất
                    # 5 (Giỏi): 100% hiệu suất
                    if skill_level == 0:
                        efficiency = 0  # 0% efficiency
                    elif skill_level == 1:
                        efficiency = 30  # 30% efficiency
                    elif skill_level == 2:
                        efficiency = 50  # 50% hiệu suất
                    elif skill_level == 3:
                        efficiency = 65  # 65% hiệu suất
                    elif skill_level == 4:
                        efficiency = 85  # 85% hiệu suất
                    else:  # skill_level == 5
                        efficiency = 100  # 100% efficiency
                    
                    # Calculate actual time using standard formula: SAM / (efficiency/100)
                    # This ensures consistency across all calculations in the system
                    if efficiency > 0:
                        actual_time = operation['sam'] / (efficiency / 100)
                    else:
                        actual_time = float('inf')  # Impossible to perform
                    
                    # Create assignment with accurate time calculation
                    assignment = {
                        'worker': assigned_worker_name,
                        'operation': operation['name'],
                        'sam': operation['sam'],
                        'actual_time': actual_time
                    }
                    
                    # Add to assignments and track assigned worker
                    self.main_app.assignments.append(assignment)
                    assigned_workers_set.add(assigned_worker_name)
        
        return assigned_workers_set
    
    def _calculate_worker_operation_times(self) -> Dict[str, Dict[str, float]]:
        """
        Step 1: Calculate actual time for each worker on each operation
        actual time = SAM / (efficiency / 100)
        """
        times = {}
        
        # Get assigned workers to exclude them from calculation
        assigned_workers = set()
        for operation in self.main_app.operations:
            assigned_worker_name = operation.get('assigned_worker', '')
            if assigned_worker_name:
                assigned_workers.add(assigned_worker_name)
        
        for worker in self.main_app.workers:
            worker_name = worker['name']
            
            # Skip assigned workers
            if worker_name in assigned_workers:
                continue
                
            times[worker_name] = {}
            
            # Get worker's difficulty handling capability
            worker_difficulty = worker.get('difficulty_handling', 'Dễ')
            
            for operation in self.main_app.operations:
                op_name = operation['name']
                machine_type = operation.get('machine', '')
                op_difficulty = operation.get('difficulty', 'Dễ')
                
                # Check if worker can handle this operation based on difficulty level
                if not self._can_handle_difficulty(worker_difficulty, op_difficulty):
                    # Worker cannot handle this difficulty level
                    times[worker_name][op_name] = float('inf')  # Impossible to perform
                    continue
                
                # Get worker skill level for this machine type (0-5)
                skill_level = worker['skills'].get(machine_type, 0)
                
                # Convert skill level to efficiency percentage
                # Skill levels: 0=Can't use, 1=Learning, 2=Basic, 3=Average, 4=Good, 5=Excellent
                # Updated scale according to new requirements:
                # 0 (Không biết dùng): 0% hiệu suất
                # 1 (Đang học): 30% hiệu suất
                # 2 (Cơ bản): 50% hiệu suất
                # 3 (Trung bình): 65% hiệu suất
                # 4 (Khá): 85% hiệu suất
                # 5 (Giỏi): 100% hiệu suất
                if skill_level == 0:
                    efficiency = 0  # 0% efficiency
                elif skill_level == 1:
                    efficiency = 30  # 30% efficiency
                elif skill_level == 2:
                    efficiency = 50  # 50% hiệu suất
                elif skill_level == 3:
                    efficiency = 65  # 65% hiệu suất
                elif skill_level == 4:
                    efficiency = 85  # 85% hiệu suất
                else:  # skill_level == 5
                    efficiency = 100  # 100% efficiency
                
                # Calculate actual time
                if efficiency > 0:
                    actual_time = operation['sam'] / (efficiency / 100)
                else:
                    actual_time = float('inf')  # Impossible to perform
                    
                times[worker_name][op_name] = actual_time
        
        return times
    
    def _can_handle_difficulty(self, worker_difficulty: str, op_difficulty: str) -> bool:
        """
        Check if worker can handle operation based on difficulty levels
        """
        # Define difficulty hierarchy
        difficulty_levels = {
            'Dễ': 1,
            'Trung bình': 2,
            'Cao': 3
        }
        
        worker_level = difficulty_levels.get(worker_difficulty, 1)
        op_level = difficulty_levels.get(op_difficulty, 1)
        
        # Worker can handle operation if their capability is equal or higher than operation difficulty
        return worker_level >= op_level
    
    def _calculate_operation_worker_requirements(self) -> Dict[str, float]:
        """
        Step 2: Calculate required workers for each operation
        Required workers = Total workers * Operation SAM / Total SAM
        """
        # Calculate total SAM
        total_sam = sum(op['sam'] for op in self.main_app.operations)
        total_workers = len(self.main_app.workers)
        
        if total_workers > 0 and total_sam > 0:
            requirements = {}
            for operation in self.main_app.operations:
                op_name = operation['name']
                # Calculate required workers for this operation
                required = (total_workers * operation['sam']) / total_sam
                # Round to nearest integer, but exclude values below 0.5
                if required >= 0.5:
                    required = round(required)
                else:
                    required = 0
                # Ensure we don't assign more than 3 workers to any single operation initially
                # (Leave room for optimization)
                required = min(required, 3)
                requirements[op_name] = required
        else:
            # Default to 1 worker per operation if calculation fails
            requirements = {op['name']: 1 for op in self.main_app.operations}
        
        return requirements
    
    def _calculate_target_output_and_takt_time(self) -> tuple:
        """
        Step 3: Calculate target hourly output and takt time
        Takt time = Total SAM / Total workers
        Target hourly output = 3600 / Takt time
        """
        total_sam = sum(op['sam'] for op in self.main_app.operations)
        total_workers = len(self.main_app.workers)
        
        if total_workers > 0:
            takt_time = total_sam / total_workers
            target_hourly_output = 3600 / takt_time if takt_time > 0 else 0
        else:
            takt_time = 0
            target_hourly_output = 0
        
        return target_hourly_output, takt_time
    
    def _allocate_workers_to_operations(self, worker_operation_times: Dict[str, Dict[str, float]], 
                                       operation_worker_requirements: Dict[str, float]):
        """
        Step 4: Allocate workers to operations based on requirements and worker capabilities
        Each operation should have enough workers to meet target output before moving to the next operation
        """
        # Track which workers are assigned to which operations
        worker_assignments = {worker['name']: [] for worker in self.main_app.workers}
        operation_assignments = {op['name']: [] for op in self.main_app.operations}
        
        # Populate assignments for already assigned workers (priority assignments)
        for assignment in self.main_app.assignments:
            worker_assignments[assignment['worker']].append(assignment)
            operation_assignments[assignment['operation']].append(assignment)
        
        # Get assigned workers to track them
        pre_assigned_workers = set()
        pre_assigned_operations = set()
        for operation in self.main_app.operations:
            assigned_worker_names = operation.get('assigned_workers', ['', '', '', ''])
            for assigned_worker_name in assigned_worker_names:
                if assigned_worker_name:
                    pre_assigned_workers.add(assigned_worker_name)
                    pre_assigned_operations.add(operation['name'])
        
        # Define special machine types that should be handled last
        special_machines = ["Máy chuyên dụng", "Phụ/Ủi"]
        
        # Count skilled workers for each machine type (excluding special machines and assigned workers)
        machine_skilled_workers = {}
        
        # Get all machine types from operations
        all_machine_types = set(op.get('machine', '') for op in self.main_app.operations if op.get('machine', ''))
        
        # Count skilled workers for each machine type
        for machine_type in all_machine_types:
            if machine_type not in special_machines:  # Exclude special machines from scarcity calculation
                skilled_count = 0
                for worker in self.main_app.workers:
                    # Skip assigned workers
                    if worker['name'] in pre_assigned_workers:
                        continue
                    skill_level = worker['skills'].get(machine_type, 0)
                    if skill_level > 0:  # Worker has some skill with this machine
                        skilled_count += 1
                machine_skilled_workers[machine_type] = skilled_count
        
        # Create a list of operations sorted by machine scarcity (least skilled workers first) and SAM (highest first)
        def operation_priority_key(operation):
            machine_type = operation.get('machine', '')
            sam_value = operation['sam']
            
            # Special machines go last (assign a high value for skilled workers)
            if machine_type in special_machines:
                return (float('inf'), -sam_value)  # Keep them last but sort by SAM descending
            
            # Regular machines sorted by scarcity (fewer skilled workers first) then by SAM (highest first)
            scarcity = machine_skilled_workers.get(machine_type, 0)
            return (scarcity, -sam_value)  # First by scarcity, then by SAM (descending)
        
        # Sort operations by priority
        sorted_operations = sorted(self.main_app.operations, key=operation_priority_key)
        
        # Process operations in order of priority
        for operation in sorted_operations:
            op_name = operation['name']
            
            # Check if operation already has pre-assigned worker
            if op_name in pre_assigned_operations:
                # Skip allocation for pre-assigned operations
                continue
                
            op_difficulty = operation.get('difficulty', 'Dễ')
            machine_type = operation.get('machine', '')
            
            # Get required workers for this operation
            required_workers = operation_worker_requirements.get(op_name, 1)
            
            # Skip if no workers required
            if required_workers <= 0:
                continue
            
            # Find eligible workers (those with skill > 0 for this machine type AND can handle difficulty)
            eligible_workers = [
                worker for worker in self.main_app.workers 
                if (worker['skills'].get(machine_type, 0) > 0 and 
                    self._can_handle_difficulty(worker.get('difficulty_handling', 'Dễ'), op_difficulty) and
                    worker['name'] not in pre_assigned_workers)
            ]
            
            # If no eligible workers, use all non-pre-assigned workers who can handle the difficulty
            if not eligible_workers:
                eligible_workers = [
                    worker for worker in self.main_app.workers 
                    if (self._can_handle_difficulty(worker.get('difficulty_handling', 'Dễ'), op_difficulty) and
                        worker['name'] not in pre_assigned_workers)
                ]
            
            # Sort eligible workers by skill level (highest first) then by number of assignments (fewer first)
            eligible_workers.sort(key=lambda w: (
                -w['skills'].get(machine_type, 0),  # Highest skill level first
                len(worker_assignments[w['name']])  # Fewer operations first
            ))
            
            # Assign required number of workers to this operation
            assigned_count = 0
            for worker in eligible_workers:
                if assigned_count >= required_workers:
                    break
                
                # Check if worker already has 3 operations
                if len(worker_assignments[worker['name']]) >= 3:
                    continue
                
                # Check adjacency constraint (except for special machines)
                if not self._is_operation_adjacent(worker_assignments[worker['name']], operation):
                    continue
                
                # Check if the actual time is valid (not infinite)
                actual_time = worker_operation_times[worker['name']][op_name]
                if not np.isfinite(actual_time):
                    continue
                
                # Assign worker to operation
                assignment = {
                    'worker': worker['name'],
                    'operation': op_name,
                    'sam': operation['sam'],
                    'actual_time': actual_time
                }
                
                self.main_app.assignments.append(assignment)
                worker_assignments[worker['name']].append(assignment)
                operation_assignments[op_name].append(assignment)
                assigned_count += 1
        
        # Handle remaining unassigned workers (if any)
        self._assign_remaining_workers(worker_assignments, operation_assignments, worker_operation_times)
    
    def _is_operation_adjacent(self, worker_assignments: List[Dict], new_operation: Dict) -> bool:
        """
        Check if new operation is adjacent to worker's current assignments
        Special machines (Máy chuyên dụng, Phụ/Ủi) are exempt from this constraint
        """
        special_machines = ["Máy chuyên dụng", "Phụ/Ủi"]
        new_machine = new_operation.get('machine', '')
        
        # Exempt special machines
        if new_machine in special_machines:
            return True
        
        # If worker has no assignments, operation is always adjacent
        if not worker_assignments:
            return True
        
        # Find positions of current assignments
        current_ops = [assignment['operation'] for assignment in worker_assignments]
        current_positions = []
        
        for i, operation in enumerate(self.main_app.operations):
            if operation['name'] in current_ops:
                current_positions.append(i)
        
        # Find position of new operation
        new_position = -1
        for i, operation in enumerate(self.main_app.operations):
            if operation['name'] == new_operation['name']:
                new_position = i
                break
        
        # Check if new operation is adjacent (within 1 position) to any current assignment
        for pos in current_positions:
            if abs(new_position - pos) <= 1:
                return True
        
        return False
    
    def _assign_remaining_workers(self, worker_assignments: Dict, operation_assignments: Dict, 
                                  worker_operation_times: Dict[str, Dict[str, float]]):
        """
        Assign any remaining unassigned workers to operations
        """
        # Find unassigned workers (those with no assignments)
        unassigned_workers = []
        for worker in self.main_app.workers:
            if len(worker_assignments[worker['name']]) == 0:
                unassigned_workers.append(worker)
        
        if not unassigned_workers:
            return
        
        # Calculate total SAM for threshold calculation
        total_sam = sum(op['sam'] for op in self.main_app.operations)
        total_workers = len(self.main_app.workers)
        
        # Assign to operations with the lowest output
        operation_outputs = self._calculate_operation_outputs()
        sorted_ops = sorted(operation_outputs.items(), key=lambda x: x[1])
        
        for worker in unassigned_workers:
            worker_difficulty = worker.get('difficulty_handling', 'Dễ')
            
            # Try to assign to operation with lowest output
            for op_name, _ in sorted_ops:
                # Find the operation details
                operation = next((op for op in self.main_app.operations if op['name'] == op_name), None)
                if not operation:
                    continue
                
                op_difficulty = operation.get('difficulty', 'Dễ')
                
                # Check if worker can handle this operation's difficulty
                if not self._can_handle_difficulty(worker_difficulty, op_difficulty):
                    continue
                
                machine_type = operation.get('machine', '')
                
                # Check if worker has skill for this machine
                if worker['skills'].get(machine_type, 0) <= 0:
                    continue
                
                # Check if worker already has 3 operations
                if len(worker_assignments[worker['name']]) >= 3:
                    continue
                
                # Check adjacency constraint
                if not self._is_operation_adjacent(worker_assignments[worker['name']], operation):
                    continue
                
                # Check if the actual time is valid (not infinite)
                actual_time = worker_operation_times[worker['name']][op_name]
                if not np.isfinite(actual_time):
                    continue
                
                # Assign worker to operation
                assignment = {
                    'worker': worker['name'],
                    'operation': op_name,
                    'sam': operation['sam'],
                    'actual_time': actual_time
                }
                
                self.main_app.assignments.append(assignment)
                worker_assignments[worker['name']].append(assignment)
                operation_assignments[op_name].append(assignment)
                break
    
    def _move_work_between_operations(self, from_op: str, to_op: str) -> bool:
        """
        Move work from one operation to another to improve balance
        A worker can perform at most 3 operations
        DEPRECATED: This method is kept for compatibility but should not be used in current implementation
        """
        return False
    
    def _optimize_allocations(self, target_hourly_output: float):
        """
        Step 6: Optimize allocations to redistribute excess capacity from high-output operations to bottlenecks
        Only move capacity from operations exceeding target to operations below target
        Operations exceeding target must maintain at least target output after redistribution
        Bottleneck operations can receive capacity up to target output
        """
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            # Calculate current operation outputs
            operation_outputs = self._calculate_operation_outputs()
            
            if not operation_outputs:
                break
            
            # Find operations with excess capacity (>110% of target)
            excess_ops = {op: output for op, output in operation_outputs.items() 
                         if output > 1.10 * target_hourly_output}
            
            # Find bottleneck operations (<90% of target)
            bottleneck_ops = {op: output for op, output in operation_outputs.items() 
                             if output < 0.90 * target_hourly_output}
            
            # If no excess or no bottlenecks, we're done
            if not excess_ops or not bottleneck_ops:
                break
            
            # Try to move workers from excess operations to bottleneck operations
            moved = False
            for excess_op, excess_output in sorted(excess_ops.items(), key=lambda x: x[1], reverse=True):
                # Check if excess operation would still be above target after moving capacity
                # We need to ensure it stays above target output
                current_excess_output = operation_outputs[excess_op]
                
                for bottleneck_op, bottleneck_output in sorted(bottleneck_ops.items(), key=lambda x: x[1]):
                    # Try to move work between operations
                    if self._move_work_between_operations_step6(excess_op, bottleneck_op, target_hourly_output, operation_outputs):
                        moved = True
                        break
                if moved:
                    break
            
            # If no moves were made, we're done
            if not moved:
                break
            
            iteration += 1
    
    def _move_work_between_operations_step6(self, from_op: str, to_op: str, target_hourly_output: float, operation_outputs: Dict[str, float]) -> bool:
        """
        Move work from one operation to another to improve balance (Step 6 specific implementation)
        Only move capacity from operations exceeding target to operations below target
        Source operation must maintain at least target output after redistribution
        Target operation can receive capacity up to target output
        """
        # Find the operation objects
        from_operation = next((op for op in self.main_app.operations if op['name'] == from_op), None)
        to_operation = next((op for op in self.main_app.operations if op['name'] == to_op), None)
        
        if not from_operation or not to_operation:
            return False
        
        # Skip if either operation has assigned workers (do not modify pre-assigned workers)
        from_assigned_workers = from_operation.get('assigned_workers', ['', '', '', ''])
        to_assigned_workers = to_operation.get('assigned_workers', ['', '', '', ''])
        if (any(assigned_worker for assigned_worker in from_assigned_workers if assigned_worker) or
            any(assigned_worker for assigned_worker in to_assigned_workers if assigned_worker)):
            return False
        
        # Get assignments for both operations
        from_assignments = [
            assignment for assignment in self.main_app.assignments 
            if assignment['operation'] == from_op
        ]
        to_assignments = [
            assignment for assignment in self.main_app.assignments 
            if assignment['operation'] == to_op
        ]
        
        # Need at least 2 workers in from_op to consider moving one
        if len(from_assignments) <= 1:
            return False
        
        # Get current outputs
        from_output = operation_outputs.get(from_op, 0)
        to_output = operation_outputs.get(to_op, 0)
        
        # Check if from_op is actually exceeding target
        if from_output <= target_hourly_output:
            return False
        
        # Check if to_op is actually below target
        if to_output >= target_hourly_output:
            return False
        
        # Get machine types
        from_machine_type = from_operation.get('machine', '')
        to_machine_type = to_operation.get('machine', '')
        to_difficulty = to_operation.get('difficulty', 'Dễ')
        
        # Try to move the least efficient worker from from_op to to_op
        from_assignments.sort(key=lambda a: a['actual_time'], reverse=True)
        
        # Take the least efficient worker
        worker_to_move = from_assignments[-1]
        worker_name = worker_to_move['worker']
        
        # Find the worker object
        worker = next((w for w in self.main_app.workers if w['name'] == worker_name), None)
        if not worker:
            return False
        
        # Check if worker can handle to_op based on difficulty level
        worker_difficulty = worker.get('difficulty_handling', 'Dễ')
        if not self._can_handle_difficulty(worker_difficulty, to_difficulty):
            return False
        
        # Check if worker has skill for to_op machine
        if worker['skills'].get(to_machine_type, 0) <= 0:
            return False
        
        # Check if worker already has 3 operations (limit to 3 operations per worker)
        worker_assignments = [
            assignment for assignment in self.main_app.assignments 
            if assignment['worker'] == worker_name
        ]
        if len(worker_assignments) >= 3:
            return False
        
        # Check adjacency constraint
        if not self._is_operation_adjacent(worker_assignments, to_operation):
            return False
        
        # Calculate the output that would be moved
        moved_output = 3600 / worker_to_move['actual_time']
        
        # Check if from_op would still exceed target after moving this worker
        if (from_output - moved_output) < target_hourly_output:
            # Cannot move this worker as it would drop from_op below target
            return False
        
        # Check if to_op would exceed target after receiving this worker
        if (to_output + moved_output) > target_hourly_output:
            # Cannot move this worker as it would push to_op above target
            # Instead, we should only move part of the capacity, but that's complex
            # For now, we'll skip this move
            return False
        
        # Remove the assignment from from_op
        self.main_app.assignments.remove(worker_to_move)
        
        # Check if the actual time is valid (not infinite)
        if not np.isfinite(worker_to_move['actual_time']):
            # Restore the assignment and continue
            self.main_app.assignments.append(worker_to_move)
            return False
        
        # Calculate new actual time for to_op
        skill_level = worker['skills'].get(to_machine_type, 0)
        
        # Convert skill level to efficiency percentage
        # Updated scale according to new requirements:
        # 0 (Không biết dùng): 0% hiệu suất
        # 1 (Đang học): 30% hiệu suất
        # 2 (Cơ bản): 50% hiệu suất
        # 3 (Trung bình): 65% hiệu suất
        # 4 (Khá): 85% hiệu suất
        # 5 (Giỏi): 100% hiệu suất
        if skill_level == 0:
            efficiency = 0  # 0% efficiency
        elif skill_level == 1:
            efficiency = 30  # 30% efficiency
        elif skill_level == 2:
            efficiency = 50  # 50% hiệu suất
        elif skill_level == 3:
            efficiency = 65  # 65% hiệu suất
        elif skill_level == 4:
            efficiency = 85  # 85% hiệu suất
        else:  # skill_level == 5
            efficiency = 100  # 100% efficiency
        
        # Calculate actual time using standard formula: SAM / (efficiency/100)
        if efficiency > 0:
            actual_time = to_operation['sam'] / (efficiency / 100)
        else:
            actual_time = float('inf')
        
        # Check if the actual time is valid (not infinite)
        if not np.isfinite(actual_time):
            # Restore the assignment and continue
            self.main_app.assignments.append(worker_to_move)
            return False
        
        # Add new assignment for to_op
        new_assignment = {
            'worker': worker_name,
            'operation': to_op,
            'sam': to_operation['sam'],
            'actual_time': actual_time
        }
        
        self.main_app.assignments.append(new_assignment)
        return True
    
    def _calculate_operation_outputs(self) -> Dict[str, float]:
        """
        Calculate hourly output for each operation
        When a worker performs multiple operations, their output for each operation 
        is proportionally divided based on the number of operations they perform
        """
        # Group assignments by operation
        op_assignments = {}
        for assignment in self.main_app.assignments:
            op_name = assignment['operation']
            op_assignments.setdefault(op_name, []).append(assignment)
        
        # Count number of operations each worker performs
        worker_operation_count = {}
        for assignment in self.main_app.assignments:
            worker_name = assignment['worker']
            worker_operation_count[worker_name] = worker_operation_count.get(worker_name, 0) + 1
        
        # Calculate output for each operation
        operation_outputs = {}
        for op_name, assignments in op_assignments.items():
            total_output = 0
            for assignment in assignments:
                # Output = 3600 seconds / actual_time for this worker if they only did this operation
                # But since they do multiple operations, divide by number of operations they perform
                # Only include valid actual_time values (positive and finite)
                if assignment['actual_time'] > 0 and np.isfinite(assignment['actual_time']):
                    full_output = 3600 / assignment['actual_time']
                    worker_output = full_output / worker_operation_count[assignment['worker']]
                    total_output += worker_output
                # Skip invalid actual_time values (inf, nan, etc.)
            operation_outputs[op_name] = total_output
        
        return operation_outputs
    
    def _calculate_efficiency_stats(self):
        """
        Calculate efficiency statistics
        """
        # Count number of operations each worker performs
        worker_operation_count = {}
        for assignment in self.main_app.assignments:
            worker = assignment['worker']
            worker_operation_count[worker] = worker_operation_count.get(worker, 0) + 1
        
        # Calculate worker loads - when a worker performs multiple operations,
        # their time for each operation is proportionally divided
        worker_loads = {}
        for assignment in self.main_app.assignments:
            worker = assignment['worker']
            time = assignment['actual_time']
            # Only include finite time values
            if np.isfinite(time):
                # When a worker performs multiple operations, their load for each operation
                # is divided by the number of operations they perform
                worker_loads[worker] = worker_loads.get(worker, 0) + (time / worker_operation_count[worker])
        
        # Calculate statistics
        loads = [v for v in worker_loads.values() if np.isfinite(v)]
        
        self.main_app.efficiency_stats = {
            'total_operations': len(self.main_app.operations),
            'total_workers': len(self.main_app.workers),
            'max_workload': max(loads) if loads else 0,
            'min_workload': min(loads) if loads else 0,
            'avg_workload': np.mean(loads) if loads else 0,
            'std_deviation': np.std(loads) if loads else 0,
            'balance_efficiency': (
                (min(loads) / max(loads) * 100) if loads and max(loads) > 0 else 0
            )
        }
    
    def _show_balance_summary(self, takt_time: float, target_hourly_output: float):
        """
        Show balance summary dialog
        """
        # Calculate operation outputs
        operation_outputs = self._calculate_operation_outputs()
        outputs = [v for v in operation_outputs.values() if np.isfinite(v)]
        
        if outputs:
            mean_output = np.mean(outputs)
            std_dev = np.std(outputs)
            cv = (std_dev / mean_output * 100) if mean_output > 0 else 0
            bottleneck_output = min(outputs)
        else:
            mean_output = 0
            std_dev = 0
            cv = 0
            bottleneck_output = 0
        
        # Calculate worker statistics
        # Count number of operations each worker performs
        worker_operation_count = {}
        for assignment in self.main_app.assignments:
            worker = assignment['worker']
            worker_operation_count[worker] = worker_operation_count.get(worker, 0) + 1
        
        # Calculate worker loads - when a worker performs multiple operations,
        # their time for each operation is proportionally divided
        worker_loads = {}
        for assignment in self.main_app.assignments:
            worker = assignment['worker']
            time = assignment['actual_time']
            # Only include finite time values
            if np.isfinite(time):
                # When a worker performs multiple operations, their load for each operation
                # is divided by the number of operations they perform
                worker_loads[worker] = worker_loads.get(worker, 0) + (time / worker_operation_count[worker])
        
        loads = [v for v in worker_loads.values() if np.isfinite(v)]
        max_load = max(loads) if loads else 0
        min_load = min(loads) if loads else 0
        avg_load = np.mean(loads) if loads else 0
        load_cv = (np.std(loads) / avg_load * 100) if avg_load > 0 else 0
        
        # Update takt time display in UI
        working_time = float(self.main_app.balancing_tab.working_time.get()) * 60  # Convert to seconds
        target_production = working_time / takt_time if takt_time > 0 else 0
        
        self.main_app.balancing_tab.takt_time_label.config(
            text=f"Takt Time: {takt_time:.2f} giây (Sản lượng: {target_production:.0f} sản phẩm)"
        )
        
        # Prepare summary message
        summary_msg = f"Hoàn tất cân bằng chuyền!\n\n"
        summary_msg += f"Tổng số công đoạn: {len(self.main_app.operations)}\n"
        summary_msg += f"Tổng SAM: {sum(op['sam'] for op in self.main_app.operations):.2f} giây\n"
        summary_msg += f"Takt time: {takt_time:.2f} giây\n" if takt_time > 0 else ""
        summary_msg += f"Sản lượng mục tiêu: {target_hourly_output:.1f} sản phẩm/giờ\n" if target_hourly_output > 0 else ""
        summary_msg += f"Tổng số công nhân: {len(self.main_app.workers)}\n"
        summary_msg += f"Số công nhân được phân công: {len(worker_loads)}\n"
        summary_msg += f"Tải cao nhất: {max_load:.2f}s\n"
        summary_msg += f"Tải thấp nhất: {min_load:.2f}s\n"
        summary_msg += f"Tải trung bình: {avg_load:.2f}s\n"
        summary_msg += f"Độ lệch tải (CV): {load_cv:.1f}%\n"
        summary_msg += f"Hiệu suất cân bằng: {self.main_app.efficiency_stats['balance_efficiency']:.1f}%\n"
        summary_msg += f"Sản lượng bottleneck: {bottleneck_output:.1f} sản phẩm/giờ\n"
        summary_msg += f"Độ lệch sản lượng (CV): {cv:.1f}%\n"
        summary_msg += f"(Giả định mỗi công nhân làm việc 8 giờ mỗi ngày)\n"
        
        messagebox.showinfo("Hoàn Tất Cân Bằng", summary_msg)
    
    def calculate_total_sam(self):
        """Calculate total SAM of all operations"""
        return sum(op['sam'] for op in self.main_app.operations)
    
    def display_results(self):
        """Display balancing results in the UI"""
        # Clear previous results
        for item in self.main_app.balancing_tab.result_tree.get_children():
            self.main_app.balancing_tab.result_tree.delete(item)
        
        # Count number of operations each worker performs
        worker_operation_count = {}
        for assignment in self.main_app.assignments:
            worker_name = assignment['worker']
            worker_operation_count[worker_name] = worker_operation_count.get(worker_name, 0) + 1
        
        # Store results data for sorting
        self.main_app.balancing_results = []
        
        # Group assignments by operation
        operation_assignments = {}
        for assignment in self.main_app.assignments:
            op_name = assignment['operation']
            operation_assignments.setdefault(op_name, []).append(assignment)
        
        # Create a map of operation sequence
        op_sequence_map = {}
        for op in self.main_app.operations:
            op_sequence_map[op['name']] = op.get('sequence', 0)
        
        # Sort operations by sequence
        sorted_operations = sorted(operation_assignments.keys(), key=lambda x: op_sequence_map.get(x, 0))
        
        # Display results in operation sequence order
        for op_name in sorted_operations:
            assignments = operation_assignments[op_name]
            for assignment in assignments:
                # Calculate efficiency as percentage
                # Efficiency = (Standard time / Actual time) * 100
                # Higher efficiency means the worker is faster (completes task in less time)
                if assignment['actual_time'] > 0:
                    # When a worker performs multiple operations, their time for each operation
                    # is proportionally divided
                    adjusted_time = assignment['actual_time'] / worker_operation_count[assignment['worker']]
                    efficiency = (assignment['sam'] / adjusted_time) * 100
                else:
                    efficiency = 0
                
                result_data = {
                    'worker': assignment['worker'],
                    'operation': assignment['operation'],
                    'sam': assignment['sam'],
                    'efficiency': efficiency,
                    'time': assignment['actual_time'] / worker_operation_count[assignment['worker']]
                }
                
                self.main_app.balancing_results.append(result_data)
                
                self.main_app.balancing_tab.result_tree.insert('', 'end', values=(
                    assignment['worker'],
                    assignment['operation'],
                    f"{assignment['sam']:.2f}",
                    f"{efficiency:.0f}",
                    f"{assignment['actual_time'] / worker_operation_count[assignment['worker']]:.2f}"
                ))