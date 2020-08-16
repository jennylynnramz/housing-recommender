class Input_Results(db.Model):
    __tablename__ = 'input_results'

    # id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String, primary_key=True)
    results = db.Column(db.String)

    def __repr__(self):
        return str(user_input) + " :: <br><br>" + str(results)