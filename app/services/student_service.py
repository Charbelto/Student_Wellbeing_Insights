    def delete_student(self, student_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        # Enable foreign key support to cascade if configured, or manually delete
        # SQLite FK support is enabled by default in many drivers but let's be safe
        
        try:
            # Delete related records first (if no cascade)
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM wellbeing_surveys WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM submissions WHERE student_id = ?", (student_id,))
            
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
