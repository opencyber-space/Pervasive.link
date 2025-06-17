import sqlite3
import json
import logging


class WorkflowPersistence:
    def __init__(self, db_path="workflow_state.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_instances (
                workflow_id TEXT PRIMARY KEY,
                dsl_definition TEXT,
                global_settings TEXT,
                global_parameters TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_states (
                module_key TEXT,
                workflow_id TEXT,
                state TEXT,
                FOREIGN KEY (workflow_id) REFERENCES workflow_instances(workflow_id),
                PRIMARY KEY (module_key, workflow_id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_states (
                task_id TEXT PRIMARY KEY,
                module_key TEXT,
                workflow_id TEXT,
                status TEXT,
                input_data TEXT,
                output_data TEXT,
                FOREIGN KEY (module_key, workflow_id) REFERENCES module_states(module_key, workflow_id)
            )
        """)
        self.conn.commit()

    def save_workflow_instance(self, workflow_id, dsl_definition, global_settings, global_parameters):
        self.cursor.execute("""
            INSERT OR REPLACE INTO workflow_instances (workflow_id, dsl_definition, global_settings, global_parameters)
            VALUES (?, ?, ?, ?)
        """, (workflow_id, json.dumps(dsl_definition), json.dumps(global_settings), json.dumps(global_parameters)))
        self.conn.commit()

    def load_workflow_instance(self, workflow_id):
        self.cursor.execute("""
            SELECT dsl_definition, global_settings, global_parameters
            FROM workflow_instances
            WHERE workflow_id = ?
        """, (workflow_id,))
        row = self.cursor.fetchone()
        if row:
            dsl_definition, global_settings, global_parameters = row
            return (json.loads(dsl_definition), json.loads(global_settings), json.loads(global_parameters))
        return None

    def save_module_state(self, module_key, workflow_id, state):
        self.cursor.execute("""
            INSERT OR REPLACE INTO module_states (module_key, workflow_id, state)
            VALUES (?, ?, ?)
        """, (module_key, workflow_id, json.dumps(state)))
        self.conn.commit()

    def load_module_state(self, module_key, workflow_id):
        self.cursor.execute("""
            SELECT state
            FROM module_states
            WHERE module_key = ? AND workflow_id = ?
        """, (module_key, workflow_id))
        row = self.cursor.fetchone()
        if row:
            state = row[0]
            return json.loads(state)
        return None

    def save_task_state(self, task_id, module_key, workflow_id, status, input_data, output_data):
        self.cursor.execute("""
              INSERT OR REPLACE INTO task_states (task_id, module_key, workflow_id, status, input_data, output_data)
              VALUES (?, ?, ?, ?, ?, ?)
          """, (task_id, module_key, workflow_id, status, json.dumps(input_data), json.dumps(output_data)))
        self.conn.commit()

    def load_task_state(self, task_id):
        self.cursor.execute("""
            SELECT module_key, workflow_id, status, input_data, output_data
            FROM task_states
            WHERE task_id = ?
        """, (task_id,))
        row = self.cursor.fetchone()
        if row:
            module_key, workflow_id, status, input_data, output_data = row
            return (module_key, workflow_id, status, json.loads(input_data), json.loads(output_data))
        return None

    def close(self):
        self.conn.close()
